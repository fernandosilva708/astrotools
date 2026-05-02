# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint, render_template, current_app, flash
from flask_login import login_required
import requests as http
from datetime import datetime

weather_bp = Blueprint('weather', __name__)

@weather_bp.route('/')
@login_required
def index():
    """Obtém previsões meteorológicas astronómicas via Open-Meteo."""
    # Localização (Lisboa por defeito, deve ser integrada com o perfil no futuro)
    lat = 38.7169
    lon = -9.1395
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,cloud_cover,visibility,wind_speed_10m",
        "timezone": "auto",
        "forecast_days": 2
    }
    
    # Endpoint de astronomia específico (se disponível e grátis)
    # Open-Meteo tem um modelo 'ecmwf_ifs04' que é bom para nuvens
    
    try:
        resp = http.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        # Processar dados horários para o template
        hourly = data.get('hourly', {})
        times = hourly.get('time', [])
        temps = hourly.get('temperature_2m', [])
        clouds = hourly.get('cloud_cover', [])
        humidity = hourly.get('relative_humidity_2m', [])
        
        forecast = []
        now = datetime.now()
        
        for i in range(len(times)):
            f_time = datetime.fromisoformat(times[i])
            # Mostrar apenas as próximas 24 horas a partir de agora
            if f_time >= now and len(forecast) < 24:
                forecast.append({
                    "time": f_time.strftime('%H:%M'),
                    "temp": f"{temps[i]}°C",
                    "clouds": clouds[i],
                    "humidity": f"{humidity[i]}%",
                    "status": "Céu Limpo" if clouds[i] < 20 else "Nublado"
                })
        
        return render_template('weather/index.html', forecast=forecast, lat=lat, lon=lon)
        
    except Exception as e:
        flash(f'Erro ao obter dados meteorológicos: {str(e)}', 'danger')
        return render_template('weather/index.html', forecast=[], lat=lat, lon=lon)
