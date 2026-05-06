# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.utils import safe_get
from app.models import AppConfig, Location

weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/')
@login_required
def index():
    locations = Location.query.filter_by(user_id=current_user.id).all()
    return render_template('weather/index.html', locations=locations)
from app.utils import safe_get, LocationService
# ...
@weather_bp.route('/api_data')
@login_required
def api_data():
    """Obtém previsões meteorológicas astronómicas via Open-Meteo."""
    location_id = request.args.get('location_id')
    if location_id and location_id != 'default':
        location = Location.query.get(location_id)
    else:
        location = LocationService.get_current_location()

    lat = location.latitude
    lon = location.longitude

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat, "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,cloud_cover,visibility,wind_speed_10m,pressure_msl,dew_point_2m",
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
        humidity = hourly.get('relative_humidity_2m', [])
        pressure = hourly.get('pressure_msl', [])
        dew_point = hourly.get('dew_point_2m', [])
        wind_speed = hourly.get('wind_speed_10m', [])
        clouds = hourly.get('cloud_cover', [])
        
        forecast = []
        now = datetime.now()
        def estimate_seeing(clouds, wind):
            if clouds < 10 and wind < 10: return "Bom"
            if clouds < 30 and wind < 20: return "Médio"
            return "Pobre"

        def estimate_transparency(clouds):
            if clouds < 10: return "Excelente"
            if clouds < 30: return "Boa"
            return "Pobre"

        for i in range(len(times)):
            f_time = datetime.fromisoformat(times[i])
            if f_time >= now and len(forecast) < 24:
                forecast.append({
                    "time": f_time.strftime('%H:%M'),
                    "temp": f"{temps[i]}°C",
                    "humidity": f"{humidity[i]}%",
                    "pressure": f"{pressure[i]} hPa",
                    "dew_point": f"{dew_point[i]}°C",
                    "wind": f"{wind_speed[i]} km/h",
                    "clouds": clouds[i],
                    "seeing": estimate_seeing(clouds[i], wind_speed[i]),
                    "transparency": estimate_transparency(clouds[i]),
                    "status": "Céu Limpo" if clouds[i] < 20 else "Nublado"
                })
        return jsonify({
            "forecast": forecast, 
            "last_update": last_update,
            "source": "Open-Meteo"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
