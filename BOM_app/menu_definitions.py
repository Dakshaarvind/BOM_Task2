"""
menu_definitions.py — Static menu declarations for the BOM application.
Imported by main.py; each Menu/Option is constructed once at import time.
"""
from Menu import Menu
from Option import Option

# ── Main ────────────────────────────────────────────────────────────────────
menu_main = Menu('main', 'Please select one of the following options:', [
    Option("Add",                    "add(sess)"),
    Option("List / Report",          "list_objects(sess)"),
    Option("Delete",                 "delete(sess)"),
    Option("Update",                 "update(sess)"),
    Option("Reports",                "reports(sess)"),
    Option("Load boilerplate data",  "boilerplate(sess)"),
    Option("Commit",                 "sess.commit()"),
    Option("Rollback",               "session_rollback(sess)"),
    Option("Exit this application",  "pass"),
])

# ── Add sub-menu ─────────────────────────────────────────────────────────────
add_menu = Menu('add', 'What would you like to add?', [
    Option("Vendor",    "add_vendor(sess)"),
    Option("Assembly",  "add_assembly(sess)"),
    Option("PiecePart", "add_piece_part(sess)"),
    Option("Usage",     "add_usage(sess)"),
    Option("Exit",      "pass"),
])

# ── List sub-menu ─────────────────────────────────────────────────────────────
list_menu = Menu('list', 'What would you like to list?', [
    Option("All Vendors",     "list_vendors(sess)"),
    Option("All Parts",       "list_parts(sess)"),
    Option("All Assemblies",  "list_assemblies(sess)"),
    Option("All PieceParts",  "list_piece_parts(sess)"),
    Option("All Usages",      "list_usages(sess)"),
    Option("One Part detail", "show_part(sess)"),
    Option("Exit",            "pass"),
])

# ── Delete sub-menu ───────────────────────────────────────────────────────────
delete_menu = Menu('delete', 'What would you like to delete?', [
    Option("Vendor",    "delete_vendor(sess)"),
    Option("Part",      "delete_part(sess)"),
    Option("Usage",     "delete_usage(sess)"),
    Option("Exit",      "pass"),
])

# ── Update sub-menu ───────────────────────────────────────────────────────────
update_menu = Menu('update', 'What would you like to update?', [
    Option("Part name",         "update_part_name(sess)"),
    Option("Usage quantity",    "update_usage_quantity(sess)"),
    Option("Vendor name",       "update_vendor_name(sess)"),
    Option("Exit",              "pass"),
])

# ── Reports sub-menu ──────────────────────────────────────────────────────────
reports_menu = Menu('reports', 'Which report would you like to run?', [
    Option("Hierarchy report",                     "hierarchy_report(sess)"),
    Option("Assemblies with most component parts", "max_component_assemblies(sess)"),
    Option("Exit",                                 "pass"),
])

# ── Debug logging level ───────────────────────────────────────────────────────
debug_select = Menu('debug select', 'Please select a debug level:', [
    Option("Informational", "logging.INFO"),
    Option("Debug",         "logging.DEBUG"),
    Option("Error",         "logging.ERROR"),
])
