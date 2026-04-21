# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint, render_template, request, Response, current_app, flash, redirect, url_for
from flask_login import login_required
import requests as http

telescopius_bp = Blueprint('telescopius', __name__)


@telescopius_bp.route('/')
@login_required
def index():
    return render_template('telescopius/index.html')


@telescopius_bp.route('/proxy')
@login_required
def proxy():
    """Encaminha pedidos para o Telescopius.

    TODO: Encaminhar pedidos autenticados com cookie de sessão / token.
    TODO: Mapear caminhos locais para os endpoints da API do Telescopius.
    TODO: Tratar CORS e negociação de content-type.
    """
    base_url = current_app.config.get('TELESCOPIUS_BASE_URL', 'https://telescopius.com')
    path = request.args.get('path', '/')
    flash('O proxy do Telescopius ainda não está implementado.', 'info')
    return redirect(url_for('telescopius.index'))
