# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db

config_bp = Blueprint('config', __name__)

@config_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        # TODO: Implementar lógica de salvamento para perfil, senha, APIs, backup
        flash('Configurações atualizadas (simulado).', 'success')
        return redirect(url_for('config.index'))
    return render_template('config/index.html')
