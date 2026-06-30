# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from skyfield.api import Loader, Topos, Star
from datetime import datetime, timedelta
import os

planner_bp = Blueprint('planner', __name__)

# Configuração da pasta de dados local
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'ephem_data')
os.makedirs(DATA_PATH, exist_ok=True)
load_sky = Loader(DATA_PATH)
ts = load_sky.timescale()
planets = load_sky('de440.bsp')
earth = planets['earth']

# Lista simplificada de objetos Messier e brilhantes
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
    from app.utils import LocationService
    from app.models import CelestialObject

    loc = LocationService.get_current_location()
    lat = loc.latitude
    lon = loc.longitude
    
    observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lon)
    now = ts.now()
    
    # Tentar carregar objetos celestes da BD
    catalog_objs = CelestialObject.query.all()
    if not catalog_objs:
        db_catalog = CATALOG
    else:
        db_catalog = [{"name": obj.name, "ra": obj.ra, "dec": obj.dec} for obj in catalog_objs]
    
    visible_objects = []
    for obj in db_catalog:
        star = Star(ra_hours=obj['ra'], dec_degrees=obj['dec'])
        alt, az, dist = observer.at(now).observe(star).apparent().altaz()
        
        visible_objects.append({
            "name": obj['name'],
            "altitude": f"{alt.degrees:.1f}°",
            "azimuth": f"{az.degrees:.1f}°",
            "visible": alt.degrees > 10,
            "alt_deg": alt.degrees
        })
    
    visible_objects.sort(key=lambda x: x['alt_deg'], reverse=True)
    return render_template('planner/index.html', objects=visible_objects, now=datetime.now().strftime('%Y-%m-%d %H:%M'))

@planner_bp.route('/chart/<object_name>')
@login_required
def get_chart_data(object_name):
    """Gera pontos de altitude para as próximas 12 horas para um objeto."""
    from app.utils import LocationService
    from app.models import CelestialObject

    loc = LocationService.get_current_location()
    lat = loc.latitude
    lon = loc.longitude
    
    observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lon)
    
    # Procurar primeiro na base de dados
    db_obj = CelestialObject.query.filter(CelestialObject.name.ilike(object_name)).first()
    if db_obj:
        ra_val = db_obj.ra
        dec_val = db_obj.dec
    else:
        # Fallback para o catálogo estático
        obj_data = next((item for item in CATALOG if item["name"].lower() == object_name.lower()), None)
        if not obj_data:
            return {"error": "Objeto não encontrado"}, 404
        ra_val = obj_data['ra']
        dec_val = obj_data['dec']
        
    star = Star(ra_hours=ra_val, dec_degrees=dec_val)
    labels, altitudes = [], []
    start_time = datetime.utcnow()
    
    for i in range(13):
        future_time = start_time + timedelta(hours=i)
        t = ts.utc(future_time.year, future_time.month, future_time.day, future_time.hour, future_time.minute)
        alt, az, dist = observer.at(t).observe(star).apparent().altaz()
        
        labels.append((datetime.now() + timedelta(hours=i)).strftime('%H:%M'))
        altitudes.append(round(max(0, alt.degrees), 1))
        
    return {"labels": labels, "altitudes": altitudes, "object": object_name}

