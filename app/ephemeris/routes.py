# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required

ephemeris_bp = Blueprint('ephemeris', __name__)


@ephemeris_bp.route('/')
@login_required
def index():
    return render_template('ephemeris/index.html')


@ephemeris_bp.route('/calculate', methods=['POST'])
@login_required
def calculate():
    """Calcula dados de efemérides para um objeto alvo.

    TODO: Usar o Skyfield para calcular:
      - Horas de nascimento / trânsito / ocaso para dada lat/lon/altitude
      - Altitude e azimute num dado instante
      - Fase e iluminação da Lua
      - Posições planetárias
    Recebe corpo JSON: {target, lat, lon, elevation, date}
    Devolve JSON com os valores calculados.
    """
    data = request.get_json() or {}
    target = data.get('target', '')
    return jsonify({
        'target': target,
        'status': 'not_implemented',
        'message': 'Cálculo de efemérides ainda não implementado.',
    })
