# SPDX-License-Identifier: GPL-2.0-only
import requests as http
import logging
from flask_login import current_user

logger = logging.getLogger(__name__)

class LocationService:
    @staticmethod
    def get_current_location():
        """Retorna o objeto Location padrão do utilizador ou valores de fallback (Lisboa)."""
        if current_user and current_user.is_authenticated and current_user.default_location:
            return current_user.default_location
        # Fallback para Lisboa
        class FallbackLocation:
            name = "Lisboa (Default)"
            latitude = 38.7223
            longitude = -9.1393
            elevation = 45.0
        return FallbackLocation()

def safe_get(url, params=None, timeout=10):
# ... (rest of the file)
    """Executa um pedido GET de forma segura com tratamento de erros padronizado."""
    try:
        response = http.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response
    except http.exceptions.Timeout:
        logger.error(f"Timeout ao contactar {url}")
        raise Exception("O servidor remoto demorou demasiado tempo a responder.")
    except http.exceptions.HTTPError as e:
        logger.error(f"Erro HTTP {e.response.status_code} ao contactar {url}")
        raise Exception(f"Erro do serviço remoto (Código: {e.response.status_code})")
    except Exception as e:
        logger.error(f"Erro inesperado ao contactar {url}: {str(e)}")
        raise Exception("Erro de ligação ao serviço.")
