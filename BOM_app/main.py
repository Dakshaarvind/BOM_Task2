"""
main.py — Menu-driven front-end for the Bill of Materials (BOM) application.
Covers Task 2: CRUD for Vendor, Assembly, PiecePart, Usage; plus two reports:
  • Hierarchy report (recursive part-breakdown)
  • Assemblies with the greatest number of direct component parts
"""
import logging
from menu_definitions import (menu_main, add_menu, list_menu, delete_menu,
                               update_menu, reports_menu, debug_select)
from db_connection import engine, Session
from orm_base import metadata

# Importing the mapped classes registers them with SQLAlchemy's mapper
from models import Base, Vendor, Part, Assembly, PiecePart, Usage
from Option import Option
from Menu import Menu


# ════════════════════════════════════════════════════════════════════════════
# Sub-menu dispatchers
# ════════════════════════════════════════════════════════════════════════════

def add(sess):
    action = ''
    while action != add_menu.last_action():
        action = add_menu.menu_prompt()
        exec(action)


def list_objects(sess):
    action = ''
    while action != list_menu.last_action():
        action = list_menu.menu_prompt()
        exec(action)


def delete(sess):
    action = ''
    while action != delete_menu.last_action():
        action = delete_menu.menu_prompt()
        exec(action)


def update(sess):
    action = ''
    while action != update_menu.last_action():
        action = update_menu.menu_prompt()
        exec(action)


def reports(sess):
    action = ''
    while action != reports_menu.last_action():
        action = reports_menu.menu_prompt()
        exec(action)


# ════════════════════════════════════════════════════════════════════════════
# SELECT helpers  (prompt the user and return an ORM object)
# ════════════════════════════════════════════════════════════════════════════

def select_vendor(session) -> Vendor:
    """Prompt for vendor name and return the Vendor object (loops until found)."""
    while True:
        name = input("Vendor name --> ").strip()
        vendor = session.query(Vendor).filter(Vendor.vendor_name == name).first()
        if vendor:
            return vendor
        print(f"No vendor named '{name}' found. Try again.")


def select_part(session) -> Part:
    """Prompt for a part number and return the (polymorphic) Part object."""
    while True:
        pnum = input("Part number --> ").strip()
        part = session.query(Part).filter(Part.part_number == pnum).first()
        if part:
            return part
        print(f"No part with number '{pnum}' found. Try again.")


def select_assembly(session) -> Assembly:
    """Prompt for a part number and return an Assembly object."""
    while True:
        pnum = input("Assembly part number --> ").strip()
        asm = session.query(Assembly).filter(Assembly.part_number == pnum).first()
        if asm:
            return asm
        print(f"No assembly with part number '{pnum}' found. Try again.")


def select_usage(session) -> Usage:
    """Prompt for assembly + component part numbers and return the Usage."""
    while True:
        print("Identify the usage by its assembly and component part numbers.")
        asm_num  = input("  Assembly part number  --> ").strip()
        comp_num = input("  Component part number --> ").strip()
        usage = session.query(Usage).filter(
            Usage.assembly_part_number  == asm_num,
            Usage.component_part_number == comp_num,
        ).first()
        if usage:
            return usage
        print("No matching usage found. Try again.")


# ════════════════════════════════════════════════════════════════════════════
# ADD operations
# ════════════════════════════════════════════════════════════════════════════

def add_vendor(session):
    """Add a new Vendor row."""
    while True:
        name = input("New vendor name (3-80 chars) --> ").strip()
        if len(name) < 3 or len(name) > 80:
            print("Vendor name must be between 3 and 80 characters. Try again.")
            continue
        existing = session.query(Vendor).filter(Vendor.vendor_name == name).first()
        if existing:
            print(f"A vendor named '{name}' already exists. Try again.")
            continue
        vendor = Vendor(name)
        session.add(vendor)
        print(f"Vendor '{name}' added (not yet committed).")
        break


def add_assembly(session):
    """Add a new Assembly row."""
    while True:
        pnum = input("Part number (1-10 chars) --> ").strip()
        if not (1 <= len(pnum) <= 10):
            print("Part number must be 1-10 characters. Try again.")
            continue
        if session.query(Part).filter(Part.part_number == pnum).first():
            print(f"A part with number '{pnum}' already exists. Try again.")
            continue
        pname = input("Part name (3-80 chars) --> ").strip()
        if not (3 <= len(pname) <= 80):
            print("Part name must be 3-80 characters. Try again.")
            continue
        if session.query(Part).filter(Part.part_name == pname).first():
            print(f"A part named '{pname}' already exists (name must be unique). Try again.")
            continue
        asm = Assembly(pnum, pname)
        session.add(asm)
        print(f"Assembly {pnum} - '{pname}' added (not yet committed).")
        break


def add_piece_part(session):
    """Add a new PiecePart row (requires an existing Vendor)."""
    while True:
        pnum = input("Part number (1-10 chars) --> ").strip()
        if not (1 <= len(pnum) <= 10):
            print("Part number must be 1-10 characters. Try again.")
            continue
        if session.query(Part).filter(Part.part_number == pnum).first():
            print(f"A part with number '{pnum}' already exists. Try again.")
            continue
        pname = input("Part name (3-80 chars) --> ").strip()
        if not (3 <= len(pname) <= 80):
            print("Part name must be 3-80 characters. Try again.")
            continue
        if session.query(Part).filter(Part.part_name == pname).first():
            print(f"A part named '{pname}' already exists (name must be unique). Try again.")
            continue
        print("Which vendor supplies this piece part?")
        vendor = select_vendor(session)
        pp = PiecePart(pnum, pname, vendor)
        session.add(pp)
        print(f"PiecePart {pnum} - '{pname}' (vendor: {vendor.vendor_name}) added (not yet committed).")
        break


def add_usage(session):
    """Add a new Usage row (link a component Part into an Assembly)."""
    print("Select the ASSEMBLY that uses the component:")
    asm = select_assembly(session)
    print("Select the COMPONENT part that goes into that assembly:")
    comp = select_part(session)
    # Guard: a part cannot be a component of itself
    if asm.part_number == comp.part_number:
        print("Error: a part cannot be a component of itself.")
        return
    # Guard: duplicate usage
    existing = session.query(Usage).filter(
        Usage.assembly_part_number  == asm.part_number,
        Usage.component_part_number == comp.part_number,
    ).first()
    if existing:
        print(f"Usage already exists: {asm.part_number} → {comp.part_number}.")
        return
    while True:
        try:
            qty = int(input("Quantity used (1-20) --> "))
            if not (1 <= qty <= 20):
                print("Quantity must be between 1 and 20. Try again.")
                continue
            break
        except ValueError:
            print("Please enter a whole number.")
    usage = Usage(asm, comp, qty)
    session.add(usage)
    print(f"Usage {asm.part_number} → {comp.part_number} × {qty} added (not yet committed).")


# ════════════════════════════════════════════════════════════════════════════
# LIST / REPORT operations
# ════════════════════════════════════════════════════════════════════════════

def list_vendors(session):
    vendors = session.query(Vendor).order_by(Vendor.vendor_name).all()
    if not vendors:
        print("No vendors in the database.")
        return
    for v in vendors:
        print(v)


def list_parts(session):
    parts = session.query(Part).order_by(Part.part_number).all()
    if not parts:
        print("No parts in the database.")
        return
    for p in parts:
        print(p)


def list_assemblies(session):
    asms = session.query(Assembly).order_by(Assembly.part_number).all()
    if not asms:
        print("No assemblies in the database.")
        return
    for a in asms:
        print(a)


def list_piece_parts(session):
    pps = session.query(PiecePart).order_by(PiecePart.part_number).all()
    if not pps:
        print("No piece parts in the database.")
        return
    for pp in pps:
        print(pp)


def list_usages(session):
    usages = session.query(Usage).order_by(
        Usage.assembly_part_number, Usage.component_part_number).all()
    if not usages:
        print("No usages in the database.")
        return
    for u in usages:
        print(u)


def show_part(session):
    """
    Show full details for a single part.  SQLAlchemy's polymorphism means that
    if the part is a PiecePart, the returned object will have .vendor_name.
    """
    part = select_part(session)
    print(part)
    if isinstance(part, PiecePart):
        print(f"  Supplied by vendor: {part.vendor_name}")
    elif isinstance(part, Assembly):
        if part.components:
            print("  Component parts:")
            for u in part.components:
                print(f"    {u.component_part_number} × {u.usage_quantity}")
        else:
            print("  (no components defined yet)")


# ════════════════════════════════════════════════════════════════════════════
# DELETE operations
# ════════════════════════════════════════════════════════════════════════════

def delete_vendor(session):
    """
    Delete a vendor only if no PieceParts currently reference it.
    """
    vendor = select_vendor(session)
    n_pps = session.query(PiecePart).filter(
        PiecePart.vendor_name == vendor.vendor_name).count()
    if n_pps > 0:
        print(f"Cannot delete '{vendor.vendor_name}': {n_pps} piece part(s) rely on this vendor. "
              "Delete or reassign those piece parts first.")
    else:
        session.delete(vendor)
        print(f"Vendor '{vendor.vendor_name}' deleted (not yet committed).")


def delete_part(session):
    """
    Delete a part.  Fails if the part is used as a component in any assembly.
    (If it is itself an Assembly, its cascade deletes its Usage children.)
    """
    part = select_part(session)
    # Check whether this part is referenced as a *component* by some assembly
    n_parent_usages = session.query(Usage).filter(
        Usage.component_part_number == part.part_number).count()
    if n_parent_usages > 0:
        print(f"Cannot delete part '{part.part_number}': it is a component in "
              f"{n_parent_usages} assembly usage(s). Remove those usages first.")
    else:
        session.delete(part)
        print(f"Part '{part.part_number}' deleted (not yet committed).")


def delete_usage(session):
    """Delete a specific Usage row."""
    usage = select_usage(session)
    session.delete(usage)
    print(f"Usage {usage.assembly_part_number} → {usage.component_part_number} "
          "deleted (not yet committed).")


# ════════════════════════════════════════════════════════════════════════════
# UPDATE operations
# ════════════════════════════════════════════════════════════════════════════

def update_part_name(session):
    """
    Change the part name of an existing part (the primary key, part_number,
    stays the same — no FK propagation needed).
    """
    print("Select the part whose name you want to change:")
    part = select_part(session)
    while True:
        new_name = input(f"New part name for '{part.part_number}' (3-80 chars) --> ").strip()
        if not (3 <= len(new_name) <= 80):
            print("Part name must be 3-80 characters. Try again.")
            continue
        conflict = session.query(Part).filter(
            Part.part_name   == new_name,
            Part.part_number != part.part_number,
        ).first()
        if conflict:
            print(f"Part name '{new_name}' is already used by part '{conflict.part_number}'. Try again.")
            continue
        old_name       = part.part_name
        part.part_name = new_name
        print(f"Part '{part.part_number}' name changed from '{old_name}' to '{new_name}' "
              "(not yet committed).")
        break


def update_usage_quantity(session):
    """Change the quantity of a Usage row."""
    usage = select_usage(session)
    while True:
        try:
            qty = int(input(f"New quantity for usage "
                            f"{usage.assembly_part_number} → {usage.component_part_number} "
                            f"(currently {usage.usage_quantity}, range 1-20) --> "))
            if not (1 <= qty <= 20):
                print("Quantity must be 1-20. Try again.")
                continue
            break
        except ValueError:
            print("Please enter a whole number.")
    usage.usage_quantity = qty
    print(f"Usage quantity updated to {qty} (not yet committed).")


def update_vendor_name(session):
    """
    Change a vendor's name — but only if no piece parts currently rely on that vendor.
    (We are deliberately avoiding ON UPDATE CASCADE to keep things simple.)
    """
    vendor = select_vendor(session)
    n_pps = session.query(PiecePart).filter(
        PiecePart.vendor_name == vendor.vendor_name).count()
    if n_pps > 0:
        print(f"Cannot rename '{vendor.vendor_name}': {n_pps} piece part(s) reference it. "
              "Remove or reassign those piece parts first.")
        return
    while True:
        new_name = input(f"New vendor name (3-80 chars) --> ").strip()
        if not (3 <= len(new_name) <= 80):
            print("Vendor name must be 3-80 characters. Try again.")
            continue
        if session.query(Vendor).filter(Vendor.vendor_name == new_name).first():
            print(f"A vendor named '{new_name}' already exists. Try again.")
            continue
        old_name         = vendor.vendor_name
        vendor.vendor_name = new_name
        print(f"Vendor renamed from '{old_name}' to '{new_name}' (not yet committed).")
        break


# ════════════════════════════════════════════════════════════════════════════
# REPORT 1 — Hierarchy report (recursive part-breakdown)
# ════════════════════════════════════════════════════════════════════════════

def _print_hierarchy(session, part: Part, level: int):
    """
    Recursively print the part hierarchy starting at *part*, indenting by
    *level* tabs.  Each line shows: <part_number> - <part_name>
    """
    indent = "\t" * level
    print(f"{indent}{part.part_number} - {part.part_name}")
    if isinstance(part, Assembly):
        # Sort children by their component part number for a stable display
        for usage in sorted(part.components,
                            key=lambda u: u.component_part_number):
            child = usage.component      # already loaded via relationship
            _print_hierarchy(session, child, level + 1)


def hierarchy_report(session):
    """
    Prompt the user for a starting part number, then print the complete
    breakdown hierarchy in indented form.
    """
    print("Enter the part number where the hierarchy report should start.")
    part = select_part(session)
    print(f"\n--- Hierarchy report starting at {part.part_number} ---")
    _print_hierarchy(session, part, 0)
    print()


# ════════════════════════════════════════════════════════════════════════════
# REPORT 2 — Assemblies with the greatest number of direct component parts
# ════════════════════════════════════════════════════════════════════════════

def max_component_assemblies(session):
    """
    Find the maximum count of *direct* component parts across all assemblies,
    then list every assembly that ties at that maximum.
    """
    assemblies = session.query(Assembly).all()
    if not assemblies:
        print("No assemblies in the database.")
        return
    counts = {a: len(a.components) for a in assemblies}
    max_count = max(counts.values())
    winners   = [a for a, cnt in counts.items() if cnt == max_count]
    print(f"\n--- Assemblies with the most direct component parts ({max_count}) ---")
    for a in sorted(winners, key=lambda x: x.part_number):
        print(f"  {a.part_number}  {a.part_name}  ({max_count} components)")
    print()


# ════════════════════════════════════════════════════════════════════════════
# BOILERPLATE DATA  (Engine + Frame per the assignment)
# ════════════════════════════════════════════════════════════════════════════

def boilerplate(sess):
    """
    Pre-loads all Engine and Frame parts (and the Motorcycle root) so that
    there is enough data to exercise the hierarchy report and the max-component
    report right away.  The Suspension parts are intentionally omitted — those
    will be added interactively via the video demo.

    WARNING: Run this ONCE only.  Running it a second time will produce
    uniqueness constraint violations.
    """
    # ── Vendors ─────────────────────────────────────────────────────────────
    v = {}
    for name in [
        "Helical International", "Plates R Us", "Wholey Rollers",
        "Jack Daniels Belts", "Engine Accessories", "Comp USA",
        "Unharnessed at Large", "Get a Grip", "Telegraph Inc.",
        "Radio Shack", "Starbucks", "Michaels", "OSH",
    ]:
        v[name] = Vendor(name)
        sess.add(v[name])

    # ── Assemblies ───────────────────────────────────────────────────────────
    a = {}
    for pnum, pname in [
        ("0",         "Motorcycle"),
        ("1",         "Engine"),
        ("1.1",       "Transmission"),
        ("1.1.1",     "Clutch"),
        ("1.1.2",     "Variator"),
        ("1.2",       "Head"),
        ("1.3",       "Battery"),
        ("1.3.2",     "Starter"),
        ("1.3.2.1",   "Stator"),
        ("2",         "Frame"),
        ("2.1",       "Handlebars"),
        ("2.1.2",     "Throttle"),
        ("2.2",       "Seat"),
        ("2.3",       "Headlight"),
    ]:
        a[pnum] = Assembly(pnum, pname)
        sess.add(a[pnum])

    # ── Piece Parts ──────────────────────────────────────────────────────────
    pp = {}
    for pnum, pname, vendor_name in [
        ("1.1.1.1",     "Springs",          "Helical International"),
        ("1.1.1.2",     "Torque",           "Plates R Us"),
        ("1.1.2.1",     "Rollers",          "Wholey Rollers"),
        ("1.1.3",       "Belt",             "Jack Daniels Belts"),
        ("1.2.1",       "Pistons",          "Engine Accessories"),
        ("1.2.2",       "Rings",            "Engine Accessories"),
        ("1.3.1",       "ECU",              "Comp USA"),
        ("1.3.2.1.1",   "Stator Wiring",    "Unharnessed at Large"),
        ("2.1.1",       "Grips",            "Get a Grip"),
        ("2.1.2.1",     "Throttle Cables",  "Telegraph Inc."),
        ("2.1.3",       "Kill Switch",      "Radio Shack"),
        ("2.2.1",       "Foam",             "Starbucks"),
        ("2.2.2",       "Fabric",           "Michaels"),
        ("2.3.1",       "Bulb",             "OSH"),
        ("2.3.2",       "Headlight Wiring", "Unharnessed at Large"),
    ]:
        pp[pnum] = PiecePart(pnum, pname, v[vendor_name])
        sess.add(pp[pnum])

    sess.flush()   # get IDs visible before building usages

    # ── All parts in one dict for easy lookup ─────────────────────────────
    all_parts = {**a, **pp}

    # ── Usages ────────────────────────────────────────────────────────────
    usage_data = [
        # Assembly         Component            Qty
        ("0",      "1",           1),   # Motorcycle ← Engine
        ("0",      "2",           1),   # Motorcycle ← Frame
        ("1",      "1.1",         1),   # Engine ← Transmission
        ("1",      "1.2",         2),   # Engine ← Head (×2)
        ("1",      "1.3",         1),   # Engine ← Battery
        ("1.1",    "1.1.1",       1),   # Transmission ← Clutch
        ("1.1",    "1.1.2",       1),   # Transmission ← Variator
        ("1.1",    "1.1.3",       1),   # Transmission ← Belt
        ("1.1.1",  "1.1.1.1",    4),   # Clutch ← Springs (×4)
        ("1.1.1",  "1.1.1.2",    1),   # Clutch ← Torque
        ("1.1.2",  "1.1.2.1",    5),   # Variator ← Rollers (×5)
        ("1.2",    "1.2.1",       2),   # Head ← Pistons (×2)
        ("1.2",    "1.2.2",       2),   # Head ← Rings (×2)
        ("1.3",    "1.3.1",       1),   # Battery ← ECU
        ("1.3",    "1.3.2",       1),   # Battery ← Starter
        ("1.3.2",  "1.3.2.1",    1),   # Starter ← Stator
        ("1.3.2.1","1.3.2.1.1",  1),   # Stator ← Stator Wiring
        ("2",      "2.1",         1),   # Frame ← Handlebars
        ("2",      "2.2",         1),   # Frame ← Seat
        ("2",      "2.3",         1),   # Frame ← Headlight
        ("2.1",    "2.1.1",       2),   # Handlebars ← Grips (×2)
        ("2.1",    "2.1.2",       1),   # Handlebars ← Throttle
        ("2.1",    "2.1.3",       1),   # Handlebars ← Kill Switch
        ("2.1.2",  "2.1.2.1",    1),   # Throttle ← Throttle Cables
        ("2.2",    "2.2.1",       1),   # Seat ← Foam
        ("2.2",    "2.2.2",       1),   # Seat ← Fabric
        ("2.3",    "2.3.1",       1),   # Headlight ← Bulb
        ("2.3",    "2.3.2",       1),   # Headlight ← Headlight Wiring
    ]
    for asm_num, comp_num, qty in usage_data:
        sess.add(Usage(a[asm_num], all_parts[comp_num], qty))

    sess.flush()
    print("Boilerplate data for Engine and Frame loaded successfully.")


# ════════════════════════════════════════════════════════════════════════════
# SESSION ROLLBACK helper
# ════════════════════════════════════════════════════════════════════════════

def session_rollback(sess):
    confirm = Menu('confirm rollback',
                   'Are you sure you want to roll back all uncommitted changes?', [
                       Option("Yes, roll back", "sess.rollback()"),
                       Option("No, cancel",     "pass"),
                   ])
    exec(confirm.menu_prompt())


# ════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print('Starting BOM application...')
    logging.basicConfig()

    # Let the user choose the SQLAlchemy logging level
    logging_action = debug_select.menu_prompt()
    logging.getLogger("sqlalchemy.engine").setLevel(eval(logging_action))
    logging.getLogger("sqlalchemy.pool").setLevel(eval(logging_action))

    # Drop and recreate all tables (development mode — comment out for production)
    metadata.drop_all(bind=engine)
    metadata.create_all(bind=engine)

    with Session() as sess:
        main_action = ''
        while main_action != menu_main.last_action():
            main_action = menu_main.menu_prompt()
            print('Next action:', main_action)
            exec(main_action)
        sess.commit()

    print('Ending normally.')
