# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from skyfield.api import Loader, Topos, Star, EarthSatellite
from datetime import datetime
import os

ephemeris_bp = Blueprint('ephemeris', __name__)

# Configuração da pasta de dados local para dados efêmeros
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'ephem_data')
os.makedirs(DATA_PATH, exist_ok=True)
load_sky = Loader(DATA_PATH)
ts = load_sky.timescale()
planets = load_sky('de440.bsp')

@ephemeris_bp.route('/')
@login_required
def index():
    """Renderiza a página principal das efemérides."""
    return render_template('ephemeris/index.html')

@ephemeris_bp.route('/iss')
@login_required
def iss_index():
    """Renderiza a página das efemérides da ISS."""
    return render_template('ephemeris/iss.html')

@ephemeris_bp.route('/update_ephemeris', methods=['POST'])
@login_required
def update_ephemeris():
    """Verifica ou atualiza os ficheiros de dados astronómicos localmente."""
    bsp_path = os.path.join(DATA_PATH, 'de440.bsp')
    # Se o ficheiro já existir e tiver um tamanho considerável, assume-se que está atualizado
    if os.path.exists(bsp_path) and os.path.getsize(bsp_path) > 100000000:
        return jsonify({"status": "success", "message": "Dados (.bsp) já estão atualizados localmente."})
    
    try:
        load_sky.download('de440.bsp')
        return jsonify({"status": "success", "message": "Dados (.bsp) descarregados com sucesso."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro ao descarregar dados: {str(e)}"}), 500

@ephemeris_bp.route('/calculate', methods=['POST'])
@login_required
def calculate():
    """Calcula a posição (RA, Dec, Alt, Az) de um objeto a partir da localização fornecida."""
    data = request.get_json() or {}
    target = data.get('target', '').strip()
    lat = float(data.get('lat') or 0.0)
    lon = float(data.get('lon') or 0.0)
    elevation = float(data.get('elevation') or 0.0)
    date_str = data.get('date', '')
    
    if not target:
        return jsonify({"status": "error", "message": "Alvo em falta."}), 400
        
    try:
        if date_str:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
        else:
            dt = datetime.utcnow()
    except Exception:
        dt = datetime.utcnow()
        
    # Usar 22:00 UTC/Local da data especificada como hora de referência de observação noturna
    t = ts.utc(dt.year, dt.month, dt.day, 22, 0, 0)
    
    # Criar observador
    observer = planets['earth'] + Topos(latitude_degrees=lat, longitude_degrees=lon, elevation_m=elevation)
    
    # Mapeamento em português/inglês para os corpos do sistema solar no arquivo de efemérides
    solar_system_map = {
        'sun': 'sun',
        'sol': 'sun',
        'moon': 'moon',
        'lua': 'moon',
        'mercury': 'mercury barycenter',
        'mercurio': 'mercury barycenter',
        'venus': 'venus barycenter',
        'mars': 'mars barycenter',
        'marte': 'mars barycenter',
        'jupiter': 'jupiter barycenter',
        'saturn': 'saturn barycenter',
        'saturno': 'saturn barycenter',
        'uranus': 'uranus barycenter',
        'urano': 'uranus barycenter',
        'neptune': 'neptune barycenter',
        'netuno': 'neptune barycenter',
    }
    
    target_lower = target.lower()
    distance_str = "N/A"
    
    if target_lower in solar_system_map:
        body_name = solar_system_map[target_lower]
        try:
            target_body = planets[body_name]
            astrometric = observer.at(t).observe(target_body)
            apparent = astrometric.apparent()
            ra, dec, distance = apparent.radec()
            alt, az, _ = apparent.altaz()
            distance_str = f"{distance.au:.6f} AU"
        except Exception as e:
            return jsonify({"status": "error", "message": f"Erro no cálculo do sistema solar: {str(e)}"}), 500
    else:
        # Tentar procurar no catálogo de objetos brilhantes do planeador
        from app.planner.routes import CATALOG
        found = None
        for obj in CATALOG:
            if target_lower in obj['name'].lower():
                found = obj
                break
        
        if found:
            target_body = Star(ra_hours=found['ra'], dec_degrees=found['dec'])
            try:
                astrometric = observer.at(t).observe(target_body)
                apparent = astrometric.apparent()
                ra, dec, _ = apparent.radec()
                alt, az, _ = apparent.altaz()
            except Exception as e:
                return jsonify({"status": "error", "message": f"Erro no cálculo do objeto estelar: {str(e)}"}), 500
        else:
            return jsonify({"status": "error", "message": f"Alvo '{target}' não encontrado no catálogo nem no sistema solar."}), 404
            
    return jsonify({
        "status": "success",
        "target": target,
        "date": dt.strftime('%Y-%m-%d'),
        "ra": str(ra),
        "dec": str(dec),
        "alt": f"{alt.degrees:.4f}°",
        "az": f"{az.degrees:.4f}°",
        "distance": distance_str
    })

@ephemeris_bp.route('/calculate_iss', methods=['POST'])
@login_required
def calculate_iss():
    """Calcula a distância relativa em tempo real entre a ISS e um corpo do sistema solar."""
    data = request.get_json() or {}
    target = data.get('target', '').strip().lower()
    
    solar_system_map = {
        'sun': 'sun',
        'moon': 'moon',
        'mars': 'mars barycenter',
        'jupiter': 'jupiter barycenter',
        'saturn': 'saturn barycenter'
    }
    
    if target not in solar_system_map:
        return jsonify({"status": "error", "message": "Alvo inválido para comparação com a ISS."}), 400
        
    try:
        # Dados TLE da ISS (Zarya) como fallback estático
        line1 = '1 25544U 98067A   26179.80556713  .00016717  00000-0  10270-3 0  9011'
        line2 = '2 25544  51.6428  22.3789 0005722 135.1234 225.8765 15.49876543 12345'
        
        iss = EarthSatellite(line1, line2, 'ISS', ts)
        t = ts.now()
        
        # Obter posições
        target_body = planets[solar_system_map[target]]
        iss_pos = planets['earth'] + iss
        
        # Calcular distância
        diff = (target_body - iss_pos).at(t)
        distance_au = diff.distance().au
        
        return jsonify({
            "status": "success",
            "distance_au": round(distance_au, 6)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": f"Erro ao calcular distância da ISS: {str(e)}"}), 500
