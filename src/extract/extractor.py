import requests
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("DataExtractor")

class EarthquakeExtractor:
    def __init__(self):
        self.base_url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson'

    def get_earhquakes(self):
        try:
            logger.info("Solicitando sismos")
            
            max_reintentos = 3
    
            for intento in range(max_reintentos):
                try:
                    response = requests.get(url=self.base_url)
                    data = response.json()
                    count = data.get("metadata", {}).get("count", 0)
            
                    logger.info(f"Se encontraron {count} eventos sismicos")
                    return data
                except requests.exceptions.Timeout:
                    logger.warning(f"El servidor tardo mucho (Intento {intento + 1}/{max_reintentos}) Reintentano en 5 segundos")
                    time.sleep(5)
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error de conexion con la API {e}")
                    break
    
            logger.error("Se agotaron los reintentos. La API esta caida")
            return 
        except Exception as e:
            logger.error(f"Error critico en extraccion {e}")
            return None

if __name__ == "__main__":
    extractor = EarthquakeExtractor()
    data = extractor.get_earhquakes()
    print(data)