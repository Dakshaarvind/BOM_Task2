"""
models.py — SQLAlchemy ORM mapped classes for the Bill of Materials project.
Task 1 authored by teammate; this file adds __init__, __str__, and the
polymorphic discriminator column required for joined-table inheritance.
"""
from __future__ import annotations
from typing import List

from sqlalchemy import String, Integer, CheckConstraint, UniqueConstraint, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Vendor
# ---------------------------------------------------------------------------
class Vendor(Base):
    __tablename__ = 'vendors'
    __table_args__ = (
        CheckConstraint('LENGTH(vendor_name) >= 3 AND LENGTH(vendor_name) <= 80',
                        name='vendors_vendor_name_length'),
    )

    vendor_name: Mapped[str] = mapped_column(String(80), primary_key=True)

    # One vendor supplies many piece parts
    piece_parts: Mapped[List["PiecePart"]] = relationship(back_populates="vendor")

    def __init__(self, vendor_name: str):
        self.vendor_name = vendor_name

    def __str__(self):
        return f"Vendor: {self.vendor_name}"


# ---------------------------------------------------------------------------
# Part  (parent of joined-table inheritance)
# ---------------------------------------------------------------------------
class Part(Base):
    __tablename__ = 'parts'
    __table_args__ = (
        UniqueConstraint('part_name', name='parts_uk_01'),
        CheckConstraint(
            'LENGTH(part_number) >= 1 AND LENGTH(part_number) <= 10',
            name='parts_part_number_length'),
        CheckConstraint(
            'LENGTH(part_name) >= 3 AND LENGTH(part_name) <= 80',
            name='parts_part_name_length'),
    )

    part_number: Mapped[str] = mapped_column(String(10), primary_key=True)
    part_name:   Mapped[str] = mapped_column(String(80), nullable=False)
    # Discriminator column — SQLAlchemy writes 'assembly' or 'piece_part' here automatically
    part_type:   Mapped[str] = mapped_column(String(20), nullable=False)

    __mapper_args__ = {
        "polymorphic_on":       "part_type",
        "polymorphic_identity": "part",          # base identity (rarely used directly)
    }

    # A Part can appear as a component in many Usages
    assemblies_used_in: Mapped[List["Usage"]] = relationship(
        back_populates="component",
        foreign_keys="[Usage.component_part_number]",
    )

    def __init__(self, part_number: str, part_name: str):
        self.part_number = part_number
        self.part_name   = part_name

    def __str__(self):
        return f"Part [{self.part_type}]: {self.part_number} - {self.part_name}"


# ---------------------------------------------------------------------------
# Assembly  (subclass of Part via joined-table inheritance)
# ---------------------------------------------------------------------------
class Assembly(Part):
    __tablename__ = 'assemblies'

    part_number: Mapped[str] = mapped_column(
        ForeignKey('parts.part_number', ondelete='CASCADE'),
        primary_key=True,
    )

    __mapper_args__ = {"polymorphic_identity": "assembly"}

    # An Assembly is composed of many component Parts (through Usage)
    components: Mapped[List["Usage"]] = relationship(
        back_populates="assembly",
        foreign_keys="[Usage.assembly_part_number]",
        cascade="all, delete-orphan",
    )

    def __init__(self, part_number: str, part_name: str):
        super().__init__(part_number, part_name)

    def __str__(self):
        return f"Assembly: {self.part_number} - {self.part_name} ({len(self.components)} components)"


# ---------------------------------------------------------------------------
# PiecePart  (subclass of Part via joined-table inheritance)
# ---------------------------------------------------------------------------
class PiecePart(Part):
    __tablename__ = 'piece_parts'

    part_number: Mapped[str] = mapped_column(
        ForeignKey('parts.part_number', ondelete='CASCADE'),
        primary_key=True,
    )
    vendor_name: Mapped[str] = mapped_column(
        ForeignKey('vendors.vendor_name'),
        nullable=False,
    )

    __mapper_args__ = {"polymorphic_identity": "piece_part"}

    # Each PiecePart is supplied by one Vendor
    vendor: Mapped["Vendor"] = relationship(back_populates="piece_parts")

    def __init__(self, part_number: str, part_name: str, vendor: "Vendor"):
        super().__init__(part_number, part_name)
        self.vendor      = vendor
        self.vendor_name = vendor.vendor_name

    def __str__(self):
        return f"PiecePart: {self.part_number} - {self.part_name}  [vendor: {self.vendor_name}]"


# ---------------------------------------------------------------------------
# Usage  (association object for Assembly → component Part many-to-many)
# ---------------------------------------------------------------------------
class Usage(Base):
    __tablename__ = 'usages'
    __table_args__ = (
        CheckConstraint('usage_quantity >= 1 AND usage_quantity <= 20',
                        name='usages_quantity_range'),
    )

    assembly_part_number:  Mapped[str] = mapped_column(
        ForeignKey('assemblies.part_number'),
        primary_key=True,
    )
    component_part_number: Mapped[str] = mapped_column(
        ForeignKey('parts.part_number'),
        primary_key=True,
    )
    usage_quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationship up to the parent Assembly
    assembly: Mapped["Assembly"] = relationship(
        back_populates="components",
        foreign_keys=[assembly_part_number],
    )
    # Relationship to the component Part (may be Assembly or PiecePart)
    component: Mapped["Part"] = relationship(
        back_populates="assemblies_used_in",
        foreign_keys=[component_part_number],
    )

    def __init__(self, assembly: "Assembly", component: "Part", quantity: int):
        self.assembly               = assembly
        self.assembly_part_number   = assembly.part_number
        self.component              = component
        self.component_part_number  = component.part_number
        self.usage_quantity         = quantity

    def __str__(self):
        return (f"Usage: {self.assembly_part_number} uses "
                f"{self.component_part_number} × {self.usage_quantity}")
