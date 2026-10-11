import requests
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("DataExtractor")


class APIEmptyResponseError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class EarthquakeExtractor:
    def __init__(self):
        self.base_url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson'

    def get_earhquakes(self):
        try:
            logger.info("Solicitando sismos")
            
            max_reintentos = 3
            timeout = 10
    
            for intento in range(max_reintentos):
                try:
                    response = requests.get(url=self.base_url, timeout=timeout)
                    response.raise_for_status()
                    data = response.json()
                    count = data.get("metadata", {}).get("count", 0)

                    if not count:
                        raise APIEmptyResponseError("La API no devolvio informacion")
            
                    logger.info(f"Se encontraron {count} eventos sismicos")
                    return data
                except requests.exceptions.Timeout:
                    logger.warning(f"El servidor tardo mucho (Intento {intento + 1}/{max_reintentos}) Reintentano en 5 segundos")
                    time.sleep(5)
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error de conexion con la API {e}")
                except requests.exceptions.HTTPError as e:
                    logger.error(f"Error en las peticiones {e}")
                
    
            logger.error("Se agotaron los reintentos. La API esta caida")
            return
        except TypeError as e:
            logger.error(f"Error de tipado: {e}")
            return
        except ImportError as e:
            logger.error(f"Error al extraer : {e}")
        except Exception as e:
            logger.error(f"Error critico en extraccion {e}")
            return

if __name__ == "__main__":
    extractor = EarthquakeExtractor()
    data = extractor.get_earhquakes()
    print(data)