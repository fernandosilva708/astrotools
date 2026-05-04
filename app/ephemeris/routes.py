# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
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


from app.utils import LocationService

@ephemeris_bp.route('/calculate', methods=['POST'])
@login_required
def calculate():
    """Calcula a altitude e azimute de um objeto."""
    data = request.get_json() or {}
    target_name = data.get('target', '').lower()

    # Usar localização do user ou defaults
    loc = LocationService.get_current_location()
    lat = loc.latitude
    lon = loc.longitude
    elev = loc.elevation
    date_str = data.get('date', datetime.utcnow().strftime('%Y-%m-%d'))


from skyfield.api import utc, Star, load, Loader, Topos

# ... (código existente DATA_PATH, load, etc.)

from skyfield.api import utc, Star, load, Loader, Topos, Orbit
# ...
def get_mpc_body(target_name):
    """Procura e cria um objeto Orbit para um corpo menor do formato MPC."""
    mpc_file = os.path.join(DATA_PATH, 'comets_bright.txt')
    if not os.path.exists(mpc_file):
        return None
    
    with open(mpc_file, 'r') as f:
        for line in f:
            if target_name.upper() in line.upper():
                # Formato Soft00 (simplificado):
                # Campos chave: Época, Inclinação, Long. Ascendente, Argumento Periélio, Excentricidade, Periélio (q), Época Periélio
                # Exemplo: 0001P   1986 02 09.0000 162.2354 306.6148  58.9796  0.967272  0.587146  1986 02 09.4513
                try:
                    parts = line.split()
                    epoch = f"{parts[1]}-{parts[2]}-{parts[3]}"
                    incl = float(parts[4])
                    node = float(parts[5])
                    argp = float(parts[6])
                    e = float(parts[7])
                    q = float(parts[8]) # Distância do periélio em UA
                    
                    return Orbit({
                        'epoch': epoch,
                        'inclination': incl,
                        'longitude_of_ascending_node': node,
                        'argument_of_perihelion': argp,
                        'eccentricity': e,
                        'perihelion_distance': q
                    }, ts=ts, earth=earth), 'minor_body'
                except:
                    continue
    return None

def get_body_object(target_name):
    """Fábrica para retornar o objeto Skyfield apropriado."""
    target_map = {
        'sun': 'sun', 'moon': 'moon', 'mars': 'mars',
        'jupiter': 'jupiter barycenter', 'saturn': 'saturn barycenter', 'venus': 'venus'
    }
    
    if target_name in target_map:
        return planets[target_map[target_name]], 'planet'
    elif target_name == 'm42':
        return Star(ra_hours=(5, 35, 17), dec_degrees=(-5, 23, 28)), 'star'
    elif target_name == 'iss':
        return get_iss(), 'satellite'
    else:
        # Tenta procurar como corpo menor
        body = get_mpc_body(target_name)
        if body:
            return body, 'minor_body'
            
    return None, None
from app.utils import LocationService

@ephemeris_bp.route('/calculate', methods=['POST'])
@login_required
def calculate():
    """Calcula a altitude e azimute de um objeto."""
    data = request.get_json() or {}
    target_name = data.get('target', '').lower()

    # Usar localização do user ou defaults
    loc = LocationService.get_current_location()
    lat = loc.latitude
    lon = loc.longitude
    elev = loc.elevation
    date_str = data.get('date', datetime.utcnow().strftime('%Y-%m-%d'))


    body, body_type = get_body_object(target_name)
    if not body:
        return jsonify({'status': 'error', 'message': 'Objeto não suportado.'}), 400

    try:
        t = ts.utc(datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=utc))
        observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lon, elevation_m=elev)
        
        if body_type == 'satellite':
            # Cálculo específico para satélites
            difference = body - observer
            topocentric = difference.at(t)
            alt, az, distance = topocentric.altaz()
        else:
            # Cálculo para corpos celestes
            astrometric = observer.at(t).observe(body)
            alt, az, distance = astrometric.apparent().altaz()

        return jsonify({
            'status': 'success',
            'target': target_name,
            'altitude': f'{alt.degrees:.2f}°',
            'azimuth': f'{az.degrees:.2f}°',
            'distance_km': f'{distance.km:.2f}' if body_type == 'satellite' else f'{distance.au:.4f} AU'
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


def update_mpc_data():
    """Descarrega dados de asteroides brilhantes do Minor Planet Center."""
    url = "https://www.minorplanetcenter.net/iau/Ephemerides/Comets/Soft00Bright.txt"
    try:
        import requests
        resp = requests.get(url)
        with open(os.path.join(DATA_PATH, 'comets_bright.txt'), 'w') as f:
            f.write(resp.text)
        return True
    except:
        return False

@ephemeris_bp.route('/update-ephemeris', methods=['POST'])
@login_required
def update_ephemeris():
    """Atualiza ficheiros de efemérides, TLEs e dados de corpos menores."""
    results = {
        'ephem': False, 'tle': False, 'mpc': False
    }
    try:
        load.download('de440.bsp')
        load.download_delta_t()
        load.download_iers()
        results['ephem'] = True
        
        load.download('https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle', filename='stations.txt')
        results['tle'] = True
        
        results['mpc'] = update_mpc_data()
        
        return jsonify({'status': 'success', 'results': results})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
