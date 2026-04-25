# GEMINI.md

This file provides foundational mandates and project context for Gemini CLI when working in this repository.

## Project Overview
**AstroTools** is a Python Flask web application providing a suite of tools for amateur astronomers, including authentication, an image gallery with Seestar ingest, plate-solving (astrometry), ephemeris calculations, a Telescopius proxy, and rclone backup functionality.

**Target Environment:** This project is specifically designed to run on a **Raspberry Pi** running a **Linux** distribution. Development and deployment considerations should account for Raspberry Pi performance characteristics and ARM architecture.

## Status
The project is currently in the **scaffolding stage**. The directory structure and initial module files have been created, but many core implementation details are pending.

## Architecture & Tech Stack
- **Framework:** Flask (Application Factory pattern in `create_app()`).
- **Database:** SQLAlchemy with Flask-Migrate (shared models in `app/models.py`). sqlite 
- **Auth:** Flask-Login for user authentication.
- **Frontend:** template html5 up editorial, Jinja2 templates, Vanilla CSS, and JavaScript.
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

## Plano de Implementação (Próximos Passos)

### 1. Base de Dados (SQLite)
- [x] Garantir que a pasta `instance/` existe e é ignorada pelo Git.
- [x] Inicializar Flask-Migrate se necessário: `flask db init`.
- [x] Criar a migração inicial: `flask db migrate -m "Initial migration"`.
- [x] Aplicar a migração: `flask db upgrade`.
- [x] Verificar a integridade dos modelos em `app/models.py`.

### 2. Frontend (HTML5 UP Editorial)
- [x] Integrar assets do template HTML5 UP Editorial em `app/static/`:
    - [x] CSS: `main.css` e sub-assets.
    - [x] JS: `main.js`, `util.js`, `breakpoints.min.js`, `browser.min.js`.
    - [x] Fonts: FontAwesome (ícones).
- [x] Refatorar `app/templates/base.html` para seguir a estrutura do Editorial:
    - [x] Implementar Sidebar (Menu lateral).
    - [x] Implementar Header/Banner.
    - [x] Adaptar o bloco `content` para a secção principal.
- [x] Atualizar todos os templates de módulos para o novo estilo:
    - [x] `dashboard/index.html`
    - [x] `gallery/index.html` e `upload.html`
    - [x] `auth/login.html` e `register.html`
    - [x] `astrometry/index.html`
    - [x] `ephemeris/index.html` e `iss.html`
    - [x] `telescopius/index.html`
    - [x] `backup/index.html`
- [x] Integrar a lógica de tradução existente (`js/translations.js`) no novo layout.
- [x] Validar a responsividade e o comportamento em dispositivos móveis.
