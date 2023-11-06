import requests
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, jsonify
import os

load_dotenv()

ipinfo_api_token = os.getenv('IPINFOAPITOKEN')

app = Flask(__name__)

def get_current_location():
    try:
        location_url = f'http://ipinfo.io/?token={ipinfo_api_token}'
        response = requests.get(location_url)

        if response.status_code == 200:
            location_data = response.json()
            coordinates = location_data.get('loc', '').split(',')
            if len(coordinates) == 2:
                latitude, longitude = map(float, coordinates)
                return latitude, longitude
            else:
                return None, None
        else:
            return None, None
    except Exception as e:
        print(f"Error retrieving current location: {e}")
        return None, None

def get_weather(latitude, longitude):
    api_key = os.getenv('APIKEYWEATHER')
    api_url = f'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search'

    params = {
        'apikey': api_key,
        'q': f'{latitude},{longitude}'
    }

    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        location_data = response.json()
        location_key = location_data['Key']

        api_url = f'http://dataservice.accuweather.com/currentconditions/v1/{location_key}'

        params = {
            'apikey': api_key,
        }

        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            weather_data = response.json()[0]

            temperature_fahrenheit = weather_data.get('Temperature', {}).get('Imperial', {}).get('Value')

            temperature_celsius = (temperature_fahrenheit - 32) * 5 / 9

            icon = weather_data.get('WeatherIcon')
            if temperature_celsius >= 10:
                is_bikeable = True
            else:
                is_bikeable = False

            saved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            response_data = {
                "temperature": temperature_celsius,
                "icon": icon,
                "bikeable": is_bikeable,
                "location": {
                    "lat": latitude,
                    "lon": longitude
                },
                "saved_at": saved_at
            }

            return response_data
        else:
            return {'error': 'Unable to fetch weather data'}
    else:
        return {'error': 'Location not found'}

@app.route('/')
def weather():
    latitude, longitude = get_current_location()

    if latitude is not None and longitude is not None:
        weather_data = get_weather(latitude, longitude)
        return jsonify(weather_data)
    else:
        return jsonify({'error': 'Unable to retrieve current location coordinates'})

if __name__ == '__main__':
    app.run()
