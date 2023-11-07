import unittest
import requests


class TestWeatherApp(unittest.TestCase):
    base_url = 'http://127.0.0.1:5001/'  # Replace with the actual URL of your Flask app

    def test_weather_endpoint_response(self):
        endpoint = '/'

        # Make a GET request to the / endpoint
        response = requests.get(self.base_url + endpoint)

        # Check the status code (200 for success)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
