# SPDX-License-Identifier: GPL-2.0-only
from datetime import datetime
from app.weather.routes import api_data
from flask import Flask

def check_weather_alerts(user):
    """Verifica condições ideais de observação e retorna um alerta se encontradas."""
    # Simula a chamada da API (precisa de um contexto de request/user)
    # Em produção, isto seria chamado por um cronjob/worker
    data = api_data().get_json()
    
    if "error" in data:
        return None
        
    alerts = []
    # Limiares de observação
    for f in data['forecast']:
        # Se céu limpo (<20%) e seeing bom
        if f['clouds'] < 20 and f['seeing'] == "Bom":
            alerts.append(f"Alerta: Céu limpo e seeing bom previsto para às {f['time']}.")
            
    return alerts
