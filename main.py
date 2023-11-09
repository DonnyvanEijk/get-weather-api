from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from sql_client import SQLClient

load_dotenv()

api_key = os.getenv('WEATHER_API_KEY')
api_url_base = os.getenv('WEATHER_API_URL', 'https://dataservice.accuweather.com')

ipinfo_api_token = os.getenv('IPINFOAPITOKEN')

app = Flask(__name__)

db_client = SQLClient()

# Simple cache to store weather data
weather_cache = {}


def create_weather_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS weather (
        id INT AUTO_INCREMENT PRIMARY KEY,
        icon VARCHAR(255),
        lat FLOAT,
        lng FLOAT,
        saved_at DATETIME,
        temperature DECIMAL(5, 2)
    );
    """
    try:
        db_client.query_fix(create_table_query)
    except Exception as e:
        print(f"Table was not able to set error {e}")


def insert_weather_data(weather_data: dict):
    try:
        db_client.insert(
            keys=('icon', 'lat', 'lng', 'saved_at', 'temperature'),
            values=(
                weather_data['icon'],
                weather_data['location']['lat'],
                weather_data['location']['lng'],
                weather_data['saved_at'],
                weather_data['temperature']
            ),
            table='weather'
        )
    except Exception as e:
        print(f"Something went wrong with inputting the value into the database \n Error: {e}")


def get_current_location():
    try:
        location_url = f'http://ipinfo.io/?token={ipinfo_api_token}'
        response = requests.get(location_url)

        if not response.status_code == 200:
            return None, None

        location_data = response.json()
        coordinates = location_data.get('loc', '').split(',')

        if not len(coordinates) == 2:
            return None, None

        latitude, longitude = map(float, coordinates)
        return latitude, longitude
    except Exception as e:
        print(f"Server not found! Error:{e}")
        return None, None


def get_weather(latitude, longitude):
    api_url = f'{api_url_base}/locations/v1/cities/geoposition/search'
    params = {
        'apikey': api_key,
        'q': f'{latitude},{longitude}'
    }

    response = requests.get(api_url, params=params)

    if not response.status_code == 200:
        print("There seems to be an issue")
        # Handle the error appropriately

    location_data = [response.json()]
    location_key = location_data[0]['Key']
    api_url = f'{api_url_base}/currentconditions/v1/{location_key}'

    return requests.get(api_url, params=params)

def parse_datetime(saved_at_str):
    try:
        return datetime.strptime(saved_at_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None

@app.route('/')
def weather():
    create_weather_table()
    latitude, longitude = get_current_location()

    # Check if data is in the cache
    cached_data = weather_cache.get((latitude, longitude))

    if latitude is not None and longitude is not None:
        if cached_data and 'saved_at' in cached_data and isinstance(cached_data['saved_at'], str):
            cached_data['saved_at'] = parse_datetime(cached_data['saved_at'])

        if cached_data and 'saved_at' in cached_data and isinstance(cached_data['saved_at'], datetime) and datetime.now() - cached_data['saved_at'] < timedelta(hours=1):
            return jsonify(cached_data)
        else:
            weather_response = get_weather(latitude, longitude)

            if weather_response.status_code == 200:
                weather_data = weather_response.json()[0]

                temperature = weather_data['Temperature']['Metric']['Value']
                icon = weather_data['WeatherText']

                bikeable = temperature > 10 and icon == "sunny"

                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                response_data = {
                    "temperature": temperature,
                    "icon": icon,
                    "bikeable": bikeable,
                    "location": {
                        "lat": latitude,
                        "lng": longitude
                    },
                    "saved_at": current_time
                }

                # Update the cache
                weather_cache[(latitude, longitude)] = response_data

                # Insert into the database only if not in cache or if cached data is older than an hour
                if not cached_data or ('saved_at' not in cached_data) or (datetime.now() - cached_data['saved_at'] >= timedelta(hours=1)):
                    insert_weather_data(response_data)

                return jsonify(response_data)
            else:
                return jsonify({'error': 'Unable to retrieve weather data'})
    else:
        return jsonify({'error': 'Unable to retrieve current location coordinates'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
