# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from skyfield.api import load, Loader, Topos
from skyfield.sgp4lib import EarthSatellite
import os
from datetime import datetime

ephemeris_bp = Blueprint('ephemeris', __name__)

# Configuração da pasta de dados local
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'ephem_data')
os.makedirs(DATA_PATH, exist_ok=True)
load = Loader(DATA_PATH)

# Carregamento de efemérides e escala de tempo
planets = load('de440.bsp')
earth = planets['earth']
ts = load.timescale()

def get_iss():
    """Carrega o TLE da ISS a partir de ficheiro local."""
    stations_file = os.path.join(DATA_PATH, 'stations.txt')
    if not os.path.exists(stations_file):
        # Tenta descarregar se não existir
        try:
            load.download('https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle', filename='stations.txt')
        except:
            return None
        
    satellites = load.tle_file(stations_file)
    for sat in satellites:
        if sat.name == 'ISS (ZARYA)':
            return sat
    return None


@ephemeris_bp.route('/')
@login_required
def index():
    return render_template('ephemeris/index.html')


@ephemeris_bp.route('/iss')
@login_required
def iss_page():
    return render_template('ephemeris/iss.html')


@ephemeris_bp.route('/calculate', methods=['POST'])
@login_required
def calculate():
    """Calcula a altitude e azimute de um corpo celeste."""
    data = request.get_json() or {}
    target_name = data.get('target', '').lower()
    lat = data.get('lat', 0.0)
    lon = data.get('lon', 0.0)
    elev = data.get('elevation', 0.0)
    date_str = data.get('date', datetime.utcnow().strftime('%Y-%m-%d'))

    target_map = {
        'sun': 'sun', 'moon': 'moon', 'mars': 'mars',
        'jupiter': 'jupiter barycenter', 'saturn': 'saturn barycenter', 'venus': 'venus'
    }

    if target_name not in target_map:
        return jsonify({'status': 'error', 'message': 'Objeto não suportado.'}), 400

    try:
        from skyfield.api import utc
        t = ts.utc(datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=utc))
        observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lon, elevation_m=elev)
        
        body = planets[target_map[target_name]]
        astrometric = observer.at(t).observe(body)
        alt, az, distance = astrometric.apparent().altaz()

        return jsonify({
            'status': 'success',
            'target': target_name,
            'altitude': f'{alt.degrees:.2f}°',
            'azimuth': f'{az.degrees:.2f}°',
            'distance_au': f'{distance.au:.4f}'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@ephemeris_bp.route('/calculate-iss', methods=['POST'])
@login_required
def calculate_iss():
    """Calcula a posição da ISS em relação a um corpo celeste."""
    data = request.get_json() or {}
    target_name = data.get('target', '').lower()
    
    target_map = {
        'sun': 'sun', 'moon': 'moon', 'mars': 'mars',
        'jupiter': 'jupiter barycenter', 'saturn': 'saturn barycenter'
    }
    
    iss = get_iss()
    if not iss or target_name not in target_map:
        return jsonify({'status': 'error', 'message': 'ISS ou objeto não encontrado.'}), 400

    try:
        t = ts.now()
        body = planets[target_map[target_name]]
        iss_pos = iss.at(t).position.au
        body_pos = body.at(t).position.au
        
        distance = sum((a - b)**2 for a, b in zip(iss_pos, body_pos))**0.5
        
        return jsonify({
            'status': 'success',
            'distance_au': f'{distance:.4f}'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@ephemeris_bp.route('/update-ephemeris', methods=['POST'])
@login_required
def update_ephemeris():
    """Atualiza ficheiros de efemérides e TLEs."""
    try:
        load.download('de440.bsp')
        load.download_delta_t()
        load.download_iers()
        load.download('https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle', filename='stations.txt')
        return jsonify({'status': 'success', 'message': 'Efemérides e TLEs atualizados.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
