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
    """Encaminha pedidos para o Telescopius, permitindo o uso da API/Dados sem problemas de CORS ou bloqueios."""
    base_url = current_app.config.get('TELESCOPIUS_BASE_URL', 'https://telescopius.com')
    path = request.args.get('path', '')
    
    if not path.startswith('/'):
        path = '/' + path
        
    url = f"{base_url}{path}"
    
    # Filtrar argumentos para não incluir o 'path' do proxy
    params = {k: v for k, v in request.args.items() if k != 'path'}
    
    try:
        # Executar o pedido ao Telescopius
        resp = http.get(url, params=params, timeout=10)
        
        # Criar a resposta do Flask baseada na resposta do Telescopius
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]
        
        return Response(resp.content, resp.status_code, headers)
        
    except Exception as e:
        flash(f'Erro ao contactar o Telescopius: {str(e)}', 'danger')
        return redirect(url_for('telescopius.index'))
