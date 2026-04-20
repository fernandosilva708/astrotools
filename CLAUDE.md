# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**AstroTools** is a Python Flask web application providing astronomy tools for amateur astronomers. Modules: authentication, image gallery (with Seestar ingest), plate-solving (astrometry), ephemeris calculations, Telescopius proxy, rclone backup, and a main dashboard.

## Status

Project is in scaffolding stage. Directory structure and empty `__init__.py` files exist; implementation files still need to be created (see `setup.bat` for the full list).

## Architecture

Flask application factory pattern (`app/__init__.py`) with blueprints per module:

```
app/
  __init__.py          # Flask factory, registers blueprints
  models.py            # SQLAlchemy models (shared across modules)
  auth/routes.py       # User authentication
  gallery/routes.py    # Image gallery
  gallery/ingest.py    # Seestar image import logic
  astrometry/routes.py # Plate-solving
  ephemeris/routes.py  # Astronomical ephemeris calculations
  telescopius/routes.py# Proxy for Telescopius services
  backup/routes.py     # Backup via rclone
  dashboard/routes.py  # Main dashboard
  templates/           # Jinja2 templates, mirroring module structure
  static/              # CSS, JS, images
migrations/            # Alembic database migrations
tests/                 # Test suite
run.py                 # Application entry point
```

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with local settings

# Initialize database
flask db upgrade

# Run development server
python run.py
```

## Key conventions

- Each module registers as a Flask Blueprint in `app/__init__.py`
- Database models live in `app/models.py` (shared SQLAlchemy models)
- Templates follow `app/templates/<module>/` structure matching blueprint names
- Environment config via `.env` (never committed); `.env.example` as template
