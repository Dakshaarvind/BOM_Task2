"""
orm_base.py — Shared SQLAlchemy Base and metadata for the BOM project.
The schema name is read interactively so that it can be changed without
touching any other file.
"""
from models import Base

metadata = Base.metadata
