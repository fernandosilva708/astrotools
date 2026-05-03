# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.utils import safe_get
from app.models import AppConfig

weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/')
@login_required
def index():
    return render_template('weather/index.html')

@weather_bp.route('/api_data')
@login_required
def api_data():
    """Obtém previsões meteorológicas astronómicas via Open-Meteo."""
    location = current_user.default_location
    lat = location.latitude if location else 38.7169
    lon = location.longitude if location else -9.1395
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,cloud_cover,visibility,wind_speed_10m",
        "timezone": "auto", "forecast_days": 2
    }
    
    try:
        resp = safe_get(url, params=params)
        data = resp.json()
        
        # Guardar ultima atualizacao
        last_update = datetime.now().isoformat()
        config = AppConfig.query.filter_by(key='WEATHER_LAST_UPDATE').first()
        if not config:
            config = AppConfig(key='WEATHER_LAST_UPDATE', value=last_update)
            db.session.add(config)
        else:
            config.value = last_update
        db.session.commit()
        
        hourly = data.get('hourly', {})
        times = hourly.get('time', [])
        temps = hourly.get('temperature_2m', [])
        clouds = hourly.get('cloud_cover', [])
        
        forecast = []
        now = datetime.now()
        for i in range(len(times)):
            f_time = datetime.fromisoformat(times[i])
            if f_time >= now and len(forecast) < 24:
                forecast.append({
                    "time": f_time.strftime('%H:%M'),
                    "temp": f"{temps[i]}°C",
                    "clouds": clouds[i],
                    "status": "Céu Limpo" if clouds[i] < 20 else "Nublado"
                })
        return jsonify({
            "forecast": forecast, 
            "last_update": last_update,
            "source": "Open-Meteo"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
