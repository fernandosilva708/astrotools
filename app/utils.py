# SPDX-License-Identifier: GPL-2.0-only
import requests as http
import logging

logger = logging.getLogger(__name__)

def safe_get(url, params=None, timeout=10):
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
