# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint, render_template, flash, redirect, url_for, current_app
from flask_login import login_required
import subprocess
import threading

backup_bp = Blueprint('backup', __name__)

# Estado global simples para monitorizar o backup (pode ser movido para a DB no futuro)
backup_status = {"running": False, "last_result": None}


def run_rclone_task(app_context, remote, path):
    """Tarefa de background para executar o rclone."""
    global backup_status
    with app_context:
        try:
            result = subprocess.run(
                ['rclone', 'sync', path, remote, '--progress'],
                capture_output=True, text=True, timeout=600,
            )
            if result.returncode == 0:
                backup_status["last_result"] = "Sucesso: Cópia concluída."
            else:
                backup_status["last_result"] = f"Erro: {result.stderr[:200]}"
        except Exception as e:
            backup_status["last_result"] = f"Falha crítica: {str(e)}"
        finally:
            backup_status["running"] = False


@backup_bp.route('/')
@login_required
def index():
    return render_template('backup/index.html', config=current_app.config, status=backup_status)


@backup_bp.route('/run', methods=['POST'])
@login_required
def run_backup():
    """Inicia a cópia de segurança em background."""
    global backup_status
    if backup_status["running"]:
        flash('Já existe uma cópia de segurança em curso.', 'warning')
        return redirect(url_for('backup.index'))

    remote = current_app.config.get('RCLONE_REMOTE', '')
    path = current_app.config.get('RCLONE_PATH', '')
    
    if not remote or not path:
        flash('RCLONE_REMOTE e RCLONE_PATH têm de estar definidos no ficheiro .env.', 'danger')
        return redirect(url_for('backup.index'))

    backup_status["running"] = True
    backup_status["last_result"] = "Em curso..."
    
    # Iniciar thread de background
    thread = threading.Thread(
        target=run_rclone_task, 
        args=(current_app.app_context(), remote, path)
    )
    thread.start()
    
    flash('Cópia de segurança iniciada em segundo plano.', 'info')
    return redirect(url_for('backup.index'))
