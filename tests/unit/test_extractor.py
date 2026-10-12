import unittest
from unittest.mock import patch, Mock
import requests

from src.extract.extractor import EarthquakeExtractor, APIExtractionError

class TestEarthquakeExtractor(unittest.TestCase):

    @patch("src.extract.extractor.time.sleep")
    @patch("src.extract.extractor.requests.get")
    def test_http_500_reintentos_agotados(self, mock_get, mock_sleep):
        respuesta = Mock()
        respuesta.status_code = 500

        error_http = requests.exceptions.HTTPError(
            "Error HTTP 500",
            response=respuesta
        )

        mock_get.return_value.raise_for_status.side_effect = error_http

        extractor = EarthquakeExtractor()

        with self.assertRaises(APIExtractionError):
            extractor.get_earthquakes()

        self.assertEqual(mock_get.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)


    @patch("src.extract.extractor.time.sleep")
    @patch("src.extract.extractor.requests.get")
    def test_extraccion_exitosa(self, mock_get, mock_sleep):
        datos_esperados = {
            "type": "FeatureCollection",
            "metadata": {"count": 1},
            "features": [
                {
                    "type": "Feature",
                    "properties": {"mag": 2.5}
                }
            ]
        }

        mock_get.return_value.json.return_value = datos_esperados

        extractor = EarthquakeExtractor()
        resultado = extractor.get_earthquakes()

        self.assertEqual(resultado, datos_esperados)
        mock_get.assert_called_once_with(
            url=extractor.base_url,
            timeout=10
        )

        mock_sleep.assert_not_called()




if __name__ == "__main__":
    unittest.main()
