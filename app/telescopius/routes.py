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
    """Proxy requests to Telescopius.

    TODO: Forward authenticated requests with session cookie / token.
    TODO: Map local paths to Telescopius API endpoints.
    TODO: Handle CORS and content-type negotiation.
    """
    base_url = current_app.config.get('TELESCOPIUS_BASE_URL', 'https://telescopius.com')
    path = request.args.get('path', '/')
    flash('Telescopius proxy is not yet implemented.', 'info')
    return redirect(url_for('telescopius.index'))
