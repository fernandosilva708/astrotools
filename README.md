# AstroTools

A Python Flask web application providing astronomy tools for amateur astronomers. Designed to run on a local network server (Raspberry Pi or Windows PC) and accessed from any browser on the same network.

## Modules

| Module | URL | Description |
|---|---|---|
| Dashboard | `/` | Overview of images and quick actions |
| Gallery | `/gallery` | Image library with upload and Seestar ingest |
| Plate Solve | `/astrometry` | Submit images to astrometry.net for WCS plate-solving |
| Ephemeris | `/ephemeris` | Rise/set/transit and altitude calculations via Skyfield |
| Telescopius | `/telescopius` | Proxy for Telescopius planning services |
| Backup | `/backup` | Sync the upload folder to a remote via rclone |
| Auth | `/auth` | Local username/password authentication |

---

## Project Structure

```
astrotools/
├── run.py                        # Application entry point
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variable template
├── setup.bat                     # Windows scaffold helper
├── app/
│   ├── __init__.py               # Flask application factory
│   ├── models.py                 # SQLAlchemy models (User, GalleryImage, Observation)
│   ├── auth/
│   │   └── routes.py             # Login, register, logout
│   ├── gallery/
│   │   ├── routes.py             # Image list, upload, delete, ingest trigger
│   │   └── ingest.py             # Seestar folder scanner
│   ├── astrometry/
│   │   └── routes.py             # Plate-solve submission to astrometry.net
│   ├── ephemeris/
│   │   └── routes.py             # Ephemeris calculation endpoint (Skyfield)
│   ├── telescopius/
│   │   └── routes.py             # Telescopius proxy
│   ├── backup/
│   │   └── routes.py             # rclone sync runner
│   ├── dashboard/
│   │   └── routes.py             # Main dashboard
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/app.js
│   └── templates/
│       ├── base.html             # Bootstrap 5 dark layout with navbar
│       ├── auth/                 # login.html, register.html
│       ├── gallery/              # index.html, upload.html
│       ├── astrometry/           # index.html
│       ├── ephemeris/            # index.html
│       ├── telescopius/          # index.html
│       ├── backup/               # index.html
│       └── dashboard/            # index.html
├── migrations/                   # Alembic database migrations
└── tests/
    ├── __init__.py
    └── conftest.py               # pytest fixtures (in-memory SQLite)
```

### Data Models

**User** — `id`, `username`, `email`, `password_hash`, `created_at`

**GalleryImage** — `id`, `filename`, `title`, `description`, `filepath`, `thumb_path`, `user_id`, `created_at`, `ra`, `dec`, `plate_solved`, `astrometry_job_id`, `target_name`, `exposure_time`, `gain`, `captured_at`

**Observation** — `id`, `target`, `notes`, `observed_at`, `ra`, `dec`, `user_id`, `created_at`

---

## Configuration

Copy `.env.example` to `.env` and edit the values:

```env
FLASK_APP=run.py
FLASK_DEBUG=1                         # Set to 0 in production
SECRET_KEY=change-me-in-production    # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
DATABASE_URL=sqlite:///astrotools.db

GALLERY_UPLOAD_FOLDER=uploads/gallery
SEESTAR_IMPORT_PATH=                  # Absolute path to Seestar output folder

ASTROMETRY_API_KEY=                   # From nova.astrometry.net/api/
ASTROMETRY_URL=http://nova.astrometry.net/api/

TELESCOPIUS_BASE_URL=https://telescopius.com

RCLONE_REMOTE=                        # e.g. gdrive:backups/astrotools
RCLONE_PATH=                          # Absolute path to the folder to back up
```

---

## Installation on Windows 11

### Prerequisites

- Python 3.11 or later — download from [python.org](https://www.python.org/downloads/)
  - During install, check **"Add Python to PATH"**
- Git (optional) — [git-scm.com](https://git-scm.com)
- rclone (optional, for backup) — [rclone.org/downloads](https://rclone.org/downloads/)

### Steps

Open **PowerShell** or **Command Prompt**:

```powershell
# 1. Clone or download the project
git clone https://github.com/youruser/astrotools.git
cd astrotools

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env
# Open .env in Notepad and set SECRET_KEY and other values
notepad .env

# 5. Initialise the database
flask db init
flask db migrate -m "initial"
flask db upgrade

# 6. Run the development server
python run.py
```

Open your browser at `http://127.0.0.1:5000` and register a user account.

### Running on startup (Windows — optional)

Create a scheduled task to start AstroTools when Windows boots:

```powershell
# From an Administrator PowerShell
$action = New-ScheduledTaskAction -Execute "C:\path\to\astrotools\.venv\Scripts\python.exe" -Argument "C:\path\to\astrotools\run.py" -WorkingDirectory "C:\path\to\astrotools"
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName "AstroTools" -Action $action -Trigger $trigger -RunLevel Highest
```

---

## Installation on Raspberry Pi

Tested on Raspberry Pi OS (64-bit, Bookworm). Works on Pi 3B+ or newer.

### Prerequisites

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git libopenjp2-7
```

Install rclone (optional, for backup):

```bash
curl https://rclone.org/install.sh | sudo bash
```

### Steps

```bash
# 1. Clone the project
git clone https://github.com/youruser/astrotools.git
cd astrotools

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
nano .env          # Set SECRET_KEY, SEESTAR_IMPORT_PATH, etc.

# 5. Initialise the database
flask db init
flask db migrate -m "initial"
flask db upgrade

# 6. Run (development)
python run.py
```

The app will be accessible from other devices on the same network at `http://<pi-ip-address>:5000`.

Find the Pi's IP address with `hostname -I`.

### Running as a systemd service (Raspberry Pi — recommended)

This keeps AstroTools running after reboot and restarts it on crash.

```bash
# Create the service file
sudo nano /etc/systemd/system/astrotools.service
```

Paste the following (adjust paths to match your setup):

```ini
[Unit]
Description=AstroTools Flask App
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/astrotools
Environment="PATH=/home/pi/astrotools/.venv/bin"
ExecStart=/home/pi/astrotools/.venv/bin/python run.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable astrotools
sudo systemctl start astrotools

# Check status
sudo systemctl status astrotools

# View logs
sudo journalctl -u astrotools -f
```

### Production server (Raspberry Pi — optional)

For better performance, run behind Gunicorn and Nginx instead of the Flask dev server.

```bash
pip install gunicorn
```

Update the `ExecStart` line in the service file:

```ini
ExecStart=/home/pi/astrotools/.venv/bin/gunicorn -w 2 -b 0.0.0.0:5000 "app:create_app()"
```

Then configure Nginx to reverse-proxy port 80 → 5000 if you want to access without specifying the port.

---

## Running Tests

```bash
# Activate virtual environment first
source .venv/bin/activate      # Linux / Pi
.venv\Scripts\activate         # Windows

pip install pytest
pytest tests/
```

---

## External Services

| Service | Purpose | Required |
|---|---|---|
| [nova.astrometry.net](http://nova.astrometry.net) | Plate-solving API | No (feature disabled without key) |
| [telescopius.com](https://telescopius.com) | Observation planning | No |
| rclone + any remote | Backup | No |

---

## Implementation Status

The project is in scaffolding stage. All routes and templates are in place and the app starts cleanly. The following features have stubs with `TODO` comments awaiting implementation:

- **Gallery ingest** — FITS header parsing (target, exposure, gain, date) and thumbnail generation
- **Plate solving** — Full astrometry.net API flow (login → upload → poll → retrieve WCS)
- **Ephemeris** — Skyfield observer calculations (rise/set/transit, altitude/azimuth, moon phase)
- **Telescopius proxy** — Session forwarding and path mapping
- **Backup** — Server-Sent Events for live rclone progress streaming

---

## License

MIT
