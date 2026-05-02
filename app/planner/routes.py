# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from skyfield.api import Loader, Topos, Star
from datetime import datetime
import os

planner_bp = Blueprint('planner', __name__)

# Configuração da pasta de dados local
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'ephem_data')
os.makedirs(DATA_PATH, exist_ok=True)
load_sky = Loader(DATA_PATH)
ts = load_sky.timescale()
planets = load_sky('de440.bsp')
earth = planets['earth']

# Lista simplificada de objetos Messier e brilhantes (Nome, RA em horas, Dec em graus)
CATALOG = [
    {"name": "M31 Andromeda Galaxy", "ra": 0.712, "dec": 41.269},
    {"name": "M42 Orion Nebula", "ra": 5.588, "dec": -5.391},
    {"name": "M45 Pleiades", "ra": 3.790, "dec": 24.117},
    {"name": "M13 Hercules Cluster", "ra": 16.695, "dec": 36.460},
    {"name": "M51 Whirlpool Galaxy", "ra": 13.498, "dec": 47.195},
    {"name": "M81 Bode's Galaxy", "ra": 9.926, "dec": 69.065},
    {"name": "M27 Dumbbell Nebula", "ra": 19.993, "dec": 22.721},
    {"name": "M57 Ring Nebula", "ra": 18.885, "dec": 33.029},
    {"name": "M44 Beehive Cluster", "ra": 8.667, "dec": 19.667},
    {"name": "Polaris", "ra": 2.530, "dec": 89.264},
]

@planner_bp.route('/')
@login_required
def index():
    """Planeia a sessão de observação sugerindo objetos visíveis."""
    # Localização do utilizador (pode vir do perfil futuramente, para já usa Lisboa por defeito)
    # TODO: Integrar com campos de lat/lon no perfil do utilizador
    lat = 38.7169
    lon = -9.1395
    elevation = 0
    
    observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lon, elevation_m=elevation)
    now = ts.now()
    
    visible_objects = []
    
    for obj in CATALOG:
        star = Star(ra_hours=obj['ra'], dec_degrees=obj['dec'])
        astrometric = observer.at(now).observe(star)
        alt, az, distance = astrometric.apparent().altaz()
        
        # Consideramos visível se estiver acima de 10 graus do horizonte
        is_visible = alt.degrees > 10
        
        visible_objects.append({
            "name": obj['name'],
            "altitude": f"{alt.degrees:.1f}°",
            "azimuth": f"{az.degrees:.1f}°",
            "visible": is_visible,
            "alt_deg": alt.degrees
        })
    
    # Ordenar por altitude (os mais altos primeiro)
    visible_objects.sort(key=lambda x: x['alt_deg'], reverse=True)
    
    return render_template('planner/index.html', objects=visible_objects, now=datetime.now().strftime('%Y-%m-%d %H:%M'))
