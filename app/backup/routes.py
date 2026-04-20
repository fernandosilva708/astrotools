from flask import Blueprint, render_template, flash, redirect, url_for, current_app
from flask_login import login_required
import subprocess

backup_bp = Blueprint('backup', __name__)


@backup_bp.route('/')
@login_required
def index():
    return render_template('backup/index.html')


@backup_bp.route('/run', methods=['POST'])
@login_required
def run_backup():
    """Run rclone sync to back up the gallery upload folder.

    TODO: Stream rclone output via Server-Sent Events for live progress.
    TODO: Persist last-run timestamp and result to the database.
    TODO: Support scheduled / automatic backups.
    """
    remote = current_app.config.get('RCLONE_REMOTE', '')
    path = current_app.config.get('RCLONE_PATH', '')
    if not remote or not path:
        flash('RCLONE_REMOTE and RCLONE_PATH must be set in .env.', 'danger')
        return redirect(url_for('backup.index'))
    try:
        result = subprocess.run(
            ['rclone', 'sync', path, remote, '--progress'],
            capture_output=True, text=True, timeout=300,
        )
        if result.returncode == 0:
            flash('Backup completed successfully.', 'success')
        else:
            flash(f'Backup failed: {result.stderr[:300]}', 'danger')
    except FileNotFoundError:
        flash('rclone not found. Install rclone and add it to PATH.', 'danger')
    except subprocess.TimeoutExpired:
        flash('Backup timed out after 5 minutes.', 'warning')
    return redirect(url_for('backup.index'))
