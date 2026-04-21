# GEMINI.md

This file provides foundational mandates and project context for Gemini CLI when working in this repository.

## Project Overview
**AstroTools** is a Python Flask web application providing a suite of tools for amateur astronomers, including authentication, an image gallery with Seestar ingest, plate-solving (astrometry), ephemeris calculations, a Telescopius proxy, and rclone backup functionality.

**Target Environment:** This project is specifically designed to run on a **Raspberry Pi** running a **Linux** distribution. Development and deployment considerations should account for Raspberry Pi performance characteristics and ARM architecture.

## Status
The project is currently in the **scaffolding stage**. The directory structure and initial module files have been created, but many core implementation details are pending.

## Architecture & Tech Stack
- **Framework:** Flask (Application Factory pattern in `create_app()`).
- **Database:** SQLAlchemy with Flask-Migrate (shared models in `app/models.py`).
- **Auth:** Flask-Login for user authentication.
- **Frontend:** Jinja2 templates, Vanilla CSS, and JavaScript.
- **External Integrations:**
  - **Astrometry:** Integration with `nova.astrometry.net` API (or local `solve-field` if available on Pi).
  - **Ephemeris:** Calculations via `skyfield` Python library.
  - **Backup:** External integration with `rclone` (system-level dependency).
  - **Telescopius:** Proxy for external astronomy services.
- **Project Structure:**
  - `app/`: Main application logic organized by blueprints.
    - `auth/`: User authentication (routes, forms).
    - `gallery/`: Image gallery with Seestar import logic (`ingest.py`).
    - `astrometry/`: Plate-solving integration.
    - `ephemeris/`: Astronomical calculations.
    - `telescopius/`: Proxy services.
    - `backup/`: rclone-based backup management.
    - `dashboard/`: Main user dashboard.
    - `static/`: Assets (CSS, JS, images).
    - `templates/`: Jinja2 templates, mirrored by module.
  - `migrations/`: Alembic database migrations.
  - `tests/`: Test suite using `pytest`.
  - `run.py`: Application entry point.

## Development Mandates & Conventions
- **Blueprints:** Each module must be registered as a Flask Blueprint in `app/__init__.py`.
- **Models:** All SQLAlchemy models must reside in `app/models.py`.
- **Templates:** Follow the `app/templates/<module>/` structure, ensuring the directory name matches the blueprint name.
- **Environment:** Use `.env` for local configuration. Never commit the `.env` file; use `.env.example` as a template.
- **Pi-Specific Considerations:**
  - Code must be compatible with ARM architecture (Raspberry Pi).
  - Minimize resource-heavy operations in the main Flask thread; use background processes where necessary.
  - Ensure compatibility with Linux-specific paths and system tools (`rclone`, etc.).
- **Standards:** Adhere to PEP 8 for Python code and maintain clear, documented route handlers.

## Common Commands
### Setup & Development (Linux/Pi)
- **Install system dependencies:** `sudo apt update && sudo apt install rclone astrometry.net` (as needed).
- **Install Python dependencies:** `pip install -r requirements.txt`.
- **Configure environment:** `cp .env.example .env` (then edit as needed).
- **Initialize/Update Database:** `flask db upgrade`.
- **Run Development Server:** `python run.py`.

### Testing & Quality
- **Run tests:** `pytest`.
- **Linting:** `flake8 app/`.
