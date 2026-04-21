# Bill of Materials (BOM) Management System — Task 2

A Python CLI application for managing hierarchical product assemblies and their component parts, backed by PostgreSQL.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [PostgreSQL Setup](#postgresql-setup)
- [Project Setup](#project-setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Database Schema](#database-schema)
- [Features](#features)
- [Sample Data](#sample-data)

---

## Overview

This application models a Bill of Materials — a hierarchical breakdown of products into their assemblies and piece parts. You can add vendors, parts (assemblies or piece parts), and define which components make up each assembly. It supports full CRUD operations plus two reports: a recursive hierarchy view and a report of assemblies with the most direct components.

---

## Tech Stack

- **Python 3.14+**
- **PostgreSQL 10+**
- **SQLAlchemy 2.0** (ORM with joined-table inheritance)
- **psycopg2** (PostgreSQL adapter)

---

## Prerequisites

- Python 3.10 or newer
- PostgreSQL installed and running
- `pip` and `venv`

---

## PostgreSQL Setup

### 1. Install PostgreSQL

Download and install from [postgresql.org](https://www.postgresql.org/download/). During installation, note your:
- superuser password (set for the `postgres` user)
- port number (default is `5432`; this project uses `5433` by default — see [Configuration](#configuration))

### 2. Start the PostgreSQL service

**Windows (PowerShell as Administrator):**
```powershell
net start postgresql-x64-17
# Replace "17" with your installed version number
```

**macOS:**
```bash
brew services start postgresql
```

**Linux:**
```bash
sudo systemctl start postgresql
```

### 3. Create the database

Open a terminal and connect to PostgreSQL:

```bash
psql -U postgres -p 5433
```

Then create the database:

```sql
CREATE DATABASE bom_db;
\q
```

> If your PostgreSQL runs on the default port 5432, use `-p 5432` above and update `config.ini` accordingly (see [Configuration](#configuration)).

### 4. Verify the connection
### I used datagrip here, and entered some details. Create a query console under a data source: postgres. Then a pop up will ask for user & pass, remmeber what u used during postgres installation & add it. Test connection & continue. Run the above commands after.
```bash
psql -U postgres -p 5433 -d bom_db
```

If you connect successfully, the database is ready.

---

## Project Setup

### 1. Clone / download the project

```bash
cd path/to/BOM_Task2
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install sqlalchemy psycopg2-binary
```

---

## Configuration

Database credentials are stored in [BOM_app/config.ini](BOM_app/config.ini):

```ini
[credentials]
userid   = postgres (usually)
password = your password set during installation goes here
host     = localhost
port     = your port set during installation goes here
database = bom_db
```

Update any of these values to match your local PostgreSQL setup:

| Field      | Description                          |
|------------|--------------------------------------|
| `userid`   | PostgreSQL username                  |
| `password` | PostgreSQL password for that user    |
| `host`     | Hostname (use `localhost` for local) |
| `port`     | Port PostgreSQL is listening on      |
| `database` | Name of the database you created     |

---

## Running the Application

Make sure your virtual environment is activated, then:

```bash
cd BOM_app
python main.py
```

On first launch the app will:
1. Ask you to choose a logging level
2. **Drop and recreate all tables** (development behavior — your data will be wiped each run)
3. Present the main menu

> **Note:** Because the app drops and recreates tables on every startup, any data you add is only persisted until you exit (or until the next run). Use the built-in "Load boilerplate data" option to quickly repopulate example data.

---

## Database Schema

The schema uses **SQLAlchemy joined-table inheritance** so that `Assembly` and `PiecePart` both extend a common `Part` table.

```
Vendor (vendor_name PK)
  └─ supplies ──► PiecePart

Part (part_number PK, part_name, part_type)
  ├─ Assembly    (joined table, inherits Part)
  └─ PiecePart   (joined table, inherits Part + vendor_name FK)

Usage (assembly_part_number FK, component_part_number FK, usage_quantity)
  Composite PK: (assembly_part_number, component_part_number)
```

---

## Features

### Add
- Add a Vendor
- Add an Assembly
- Add a Piece Part (linked to a vendor)
- Add a Usage (link a component to an assembly with a quantity)

### List / Report
- List all Vendors, Parts, Assemblies, Piece Parts, or Usages
- Show details for a single part

### Update
- Update a Part's name
- Update a Usage's quantity
- Update a Vendor's name

### Delete
- Delete a Vendor (blocked if piece parts still reference it)
- Delete a Part (blocked if usages still reference it)
- Delete a Usage

### Reports
- **Hierarchy Report** — recursively displays the full component breakdown for any assembly
- **Max Component Parts Report** — lists assemblies ranked by number of direct components

### Transaction Control
- **Commit** — saves all pending changes to the database
- **Rollback** — discards all pending changes since the last commit

---

## Sample Data

The main menu includes a **"Load boilerplate data"** option that populates the database with a motorcycle assembly example:

- 13 vendors
- 14 assemblies (Motorcycle → Engine, Frame, Transmission, etc.)
- 15 piece parts
- 28 usage relationships

Use this to explore the hierarchy report and other features without entering data manually.
