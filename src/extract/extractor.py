import requests
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("DataExtractor")


class APIEmptyResponseError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class APIInvalidStructureError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class APIExtractionError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class EarthquakeExtractor:
    def __init__(self):
        self.base_url = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson'

    def geojson_valido(self, data: dict) -> bool:
        if not isinstance(data, dict):
            return False

        if data.get("type") != "FeatureCollection":
            return False

        if not isinstance(data.get("features"), list):
            return False

        return True

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

                    if not self.geojson_valido(data):
                        raise APIInvalidStructureError("La respuesta recibida no cumple con la estructura de un GeoJSON valido")

                    count = data.get("metadata", {}).get("count", 0)
                    logger.info(f"Estructura valida. {count} eventos sismicos encontrados")
                    return data
                
                except requests.exceptions.Timeout:
                    logger.warning(f"El servidor tardo mucho (Intento {intento}/{max_reintentos}) Reintentando ...")
                except requests.exceptions.HTTPError as e:
                    status_code = e.response.status_code
                    logger.error(f"Erros http {status_code}: {e}")

                    if 400 <= status_code < 500:
                        logger.error("Error del cliente detectado. No se realizaran mas intentos")
                        raise APIExtractionError(f"La respuesta http lanzo el codigo: {status_code}") from e
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error de conexion con la API {e}")
                    
                if intento < max_reintentos:
                    tiempo_espera = 2**intento
                    logger.info(f"Reintentando conexion en {tiempo_espera} segundos")
                    time.sleep(tiempo_espera)
                else:
                    logger.error("Se agotaron todos los reintentos disponibles")

        except APIInvalidStructureError:
            raise
        except Exception as e:
            logger.exception("Erros inesperado en la extraccion")
            raise APIExtractionError("No se pudo completar la extraccion") from e

if __name__ == "__main__":
    extractor = EarthquakeExtractor()
    try:
        data = extractor.get_earthquakes()
        print("Proceso finalizado con exito. Total de elementos en features: ", len(data.get("features", [])))
    except APIInvalidStructureError as e:
        print(f"Error de estructura: {e}")