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

weather_cache = {}


def create_weather_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS weather (
        id INT AUTO_INCREMENT PRIMARY KEY,
        icon VARCHAR(255),
        lat VARCHAR(255),
        lng VARCHAR(255),
        saved_at DATETIME,
        temperature DECIMAL(5, 2)
    );
    """
    try:
        db_client.query_fix(create_table_query)
    except Exception as e:
        return jsonify({'error': f'Table creation error: {e}'})


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
        return jsonify({'error': f'Database insertion error: {e}'})


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
    except requests.RequestException as e:
        return None, None


def get_weather(latitude, longitude):
    api_url = f'{api_url_base}/locations/v1/cities/geoposition/search'
    params = {
        'apikey': api_key,
        'q': f'{latitude},{longitude}'
    }

    try:
        response = requests.get(api_url, params=params)

        if not response.status_code == 200:
            return jsonify({'error': 'Location search error'})

        location_data = [response.json()]
        location_key = location_data[0]['Key']
        api_url = f'{api_url_base}/currentconditions/v1/{location_key}'

        return requests.get(api_url, params=params)
    except requests.RequestException as e:
        return jsonify({'error': f'Weather API request error: {e}'})


@app.route('/')
def weather():
    create_weather_table()
    latitude, longitude = get_current_location()

    if latitude is None or longitude is None:
        return jsonify({'error': 'Unable to retrieve current location coordinates'})

    cached_data = weather_cache.get((latitude, longitude))

    if cached_data and 'saved_at' in cached_data and isinstance(cached_data['saved_at'], datetime) and datetime.now() - cached_data['saved_at'] < timedelta(hours=1):
        return jsonify(cached_data)

    db_data = db_client.fetch_all(
        "SELECT * FROM weather WHERE lat = %s AND lng = %s ORDER BY saved_at DESC LIMIT 1;",
        (latitude, longitude)
    )

    if db_data:
        db_saved_at = db_data[0]['saved_at']
        if datetime.now() - db_saved_at < timedelta(hours=1):
            response_data = {
                "temperature": db_data[0]['temperature'],
                "icon": db_data[0]['icon'],
                "bikeable": db_data[0]['temperature'] > 10 and db_data[0]['icon'] == "sunny",
                "location": {"lat": latitude, "lng": longitude},
                "saved_at": db_saved_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            weather_cache[(latitude, longitude)] = response_data
            return jsonify(response_data)

    weather_response = get_weather(latitude, longitude)

    if weather_response.status_code != 200:
        return jsonify({'error': 'Unable to retrieve weather data'})

    try:
        weather_data = weather_response.json()[0]
        temperature = weather_data['Temperature']['Metric']['Value']
        icon = weather_data['WeatherText']
    except (IndexError, KeyError):
        return jsonify({'error': 'Weather data not available or in unexpected format'})

    bikeable = temperature > 10 and icon == "sunny"
    current_time = datetime.now()

    response_data = {
        "temperature": temperature,
        "icon": icon,
        "bikeable": bikeable,
        "location": {"lat": latitude, "lng": longitude},
        "saved_at": current_time,
    }

    weather_cache[(latitude, longitude)] = response_data

    if not db_data or datetime.now() - db_saved_at >= timedelta(hours=1):
        insert_weather_data(response_data)

    return jsonify(response_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
