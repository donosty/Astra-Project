import requests
import logging
import time
import json

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("DataExtractor")


class APIEmptyResponseError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class EarthquakeExtractor:
    def __init__(self):
        self.base_url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson'

    def get_earthquakes(self):
        try:
            logger.info("Solicitando sismos")
            
            max_reintentos = 3
            timeout = 10
    
            for intento in range(1, max_reintentos + 1):
                try:
                    response = requests.get(url=self.base_url, timeout=timeout)
                    response.raise_for_status()
                    data = response.json()
                    count = data.get("metadata", {}).get("count", 0)

                    if not count:
                        raise APIEmptyResponseError("La API respondio correctamente pero no devolvio registros")
            
                    logger.info(f"Se encontraron {count} eventos sismicos")
                    return data
                except requests.exceptions.Timeout:
                    logger.warning(f"El servidor tardo mucho (Intento {intento + 1}/{max_reintentos}) Reintentano en 5 segundos")
                    time.sleep(5)
                except requests.exceptions.HTTPError as e:
                    status_code = e.response.status_code
                    logger.error(f"Erros http {status_code}: {e}")

                    if 400 <= status_code < 500:
                        logger.error("Error del cliente detectado. No se realizaran mas intentos")
                        break 
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error de conexion con la API {e}")
                if intento < max_reintentos:
                    tiempo_espera = 2**intento
                    logger.info(f"Reintentando conexion en {tiempo_espera} segundos")
                    time.sleep(tiempo_espera)
                else:
                    logger.error("Se agotaron todos los reintentos disponibles")
                
    
        except TypeError as e:
            logger.error(f"Error de tipado: {e}")
        except ImportError as e:
            logger.error(f"Error al extraer : {e}")

        raise APIEmptyResponseError("No se pudo obtener informacion de la API")

if __name__ == "__main__":
    extractor = EarthquakeExtractor()
    data = extractor.get_earthquakes()
    print(data)