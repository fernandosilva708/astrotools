# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint, render_template, request, Response, current_app
from flask_login import login_required
from app.utils import safe_get

telescopius_bp = Blueprint('telescopius', __name__)

@telescopius_bp.route('/')
@login_required
def index():
    return render_template('telescopius/index.html')

@telescopius_bp.route('/proxy')
@login_required
def proxy():
    """Encaminha pedidos para o Telescopius com tratamento de erros centralizado."""
    base_url = current_app.config.get('TELESCOPIUS_BASE_URL', 'https://telescopius.com')
    path = request.args.get('path', '/')
    if not path.startswith('/'): path = '/' + path
    url = f"{base_url}{path}"
    
    params = {k: v for k, v in request.args.items() if k != 'path'}
    
    try:
        resp = safe_get(url, params=params)
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.headers.items()
                   if name.lower() not in excluded_headers]
        return Response(resp.content, resp.status_code, headers)
    except Exception as e:
        return Response(f"Erro ao contactar o Telescopius: {str(e)}", status=502)
