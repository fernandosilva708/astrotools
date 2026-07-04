# SPDX-License-Identifier: GPL-2.0-only
import requests

class SeestarController:
    """Wrapper básico para comunicação com o Seestar S50 via protocolo Alpaca/REST."""
    def __init__(self, ip_address, port=5555):
        self.ip_address = ip_address
        self.port = port
        self.base_url = f"http://{ip_address}:{port}/api/v1"
        self.client_id = 1
        self.client_transaction_id = 1

    def _get(self, device_type, endpoint, params=None):
        if params is None:
            params = {}
        params['ClientID'] = self.client_id
        params['ClientTransactionID'] = self.client_transaction_id
        self.client_transaction_id += 1
        
        try:
            resp = requests.get(f"{self.base_url}/{device_type}/0/{endpoint}", params=params, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('ErrorNumber', 0) != 0:
                    raise Exception(data.get('ErrorMessage', 'Erro desconhecido do dispositivo.'))
                return data
            return None
        except Exception as e:
            raise Exception(f"Erro ao comunicar com Seestar: {e}")

    def _put(self, device_type, endpoint, data=None):
        if data is None:
            data = {}
        data['ClientID'] = self.client_id
        data['ClientTransactionID'] = self.client_transaction_id
        self.client_transaction_id += 1
        
        try:
            resp = requests.put(f"{self.base_url}/{device_type}/0/{endpoint}", data=data, timeout=5)
            if resp.status_code == 200:
                result = resp.json()
                if result.get('ErrorNumber', 0) != 0:
                    raise Exception(result.get('ErrorMessage', 'Erro desconhecido do dispositivo.'))
                return result
            return None
        except Exception as e:
            raise Exception(f"Erro ao comunicar com Seestar: {e}")

    def get_connected(self):
        """Verifica se o telescópio está conectado."""
        try:
            resp = self._get('telescope', 'connected')
            return resp.get('Value', False) if resp else False
        except:
            return False

    def get_status(self):
        """Verifica o estado completo do dispositivo (aggregando propriedades do telescópio)."""
        if not self.get_connected():
            return None
            
        try:
            slewing = self._get('telescope', 'slewing').get('Value', False)
            tracking = self._get('telescope', 'tracking').get('Value', False)
            ra = self._get('telescope', 'rightascension').get('Value', 0.0)
            dec = self._get('telescope', 'declination').get('Value', 0.0)
            
            return {
                'connected': True,
                'slewing': slewing,
                'tracking': tracking,
                'ra': ra,
                'dec': dec
            }
        except Exception:
            return None

    def slew_to_coordinates(self, ra_hours, dec_degrees):
        """Move o telescópio para as coordenadas (RA em horas, DEC em graus)."""
        try:
            # Ativa tracking antes do slew
            self._put('telescope', 'tracking', {'Tracking': 'True'})
            
            data = {
                'RightAscension': ra_hours,
                'Declination': dec_degrees
            }
            return self._put('telescope', 'slewtocoordinatesasync', data) is not None
        except Exception as e:
            print(f"Erro no slew: {e}")
            return False

    def capture_image(self, exposure_seconds=1.0, gain=100):
        """Dispara uma captura via câmara."""
        try:
            data = {
                'Duration': exposure_seconds,
                'Light': 'True'
            }
            return self._put('camera', 'startexposure', data) is not None
        except Exception as e:
            print(f"Erro na captura: {e}")
            return False

    def abort(self):
        """Aborta movimentos."""
        try:
            return self._put('telescope', 'abortslew') is not None
        except:
            return False
            
    def park(self):
        """Estaciona o telescópio."""
        try:
            return self._put('telescope', 'park') is not None
        except:
            return False
