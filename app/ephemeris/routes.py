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
    """Calculate ephemeris data for a target object.

    TODO: Use Skyfield to compute:
      - Rise / transit / set times for given lat/lon/elevation
      - Altitude & azimuth at a given time
      - Moon phase and illumination
      - Planetary positions
    Expects JSON body: {target, lat, lon, elevation, date}
    Returns JSON with computed values.
    """
    data = request.get_json() or {}
    target = data.get('target', '')
    return jsonify({
        'target': target,
        'status': 'not_implemented',
        'message': 'Ephemeris calculation not yet implemented.',
    })
