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
    """Executa sincronização rclone para fazer cópia de segurança da pasta de carregamentos da galeria.

    TODO: Transmitir a saída do rclone via Server-Sent Events para progresso em tempo real.
    TODO: Guardar a data/hora e resultado da última execução na base de dados.
    TODO: Suportar cópias de segurança agendadas / automáticas.
    """
    remote = current_app.config.get('RCLONE_REMOTE', '')
    path = current_app.config.get('RCLONE_PATH', '')
    if not remote or not path:
        flash('RCLONE_REMOTE e RCLONE_PATH têm de estar definidos no ficheiro .env.', 'danger')
        return redirect(url_for('backup.index'))
    try:
        result = subprocess.run(
            ['rclone', 'sync', path, remote, '--progress'],
            capture_output=True, text=True, timeout=300,
        )
        if result.returncode == 0:
            flash('Cópia de segurança concluída com sucesso.', 'success')
        else:
            flash(f'Falha na cópia de segurança: {result.stderr[:300]}', 'danger')
    except FileNotFoundError:
        flash('rclone não encontrado. Instale o rclone e adicione-o ao PATH.', 'danger')
    except subprocess.TimeoutExpired:
        flash('A cópia de segurança excedeu o tempo limite de 5 minutos.', 'warning')
    return redirect(url_for('backup.index'))
