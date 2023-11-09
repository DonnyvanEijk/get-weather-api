import requests
import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from datetime import datetime
from sql_client import SQLClient

load_dotenv()

ipinfo_api_token = os.getenv('IPINFOAPITOKEN')

app = Flask(__name__)

db_client = SQLClient()

def create_weather_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS weather (
        id INT AUTO_INCREMENT PRIMARY KEY,
        bikeable BOOLEAN,
        icon VARCHAR(255),
        lat FLOAT,
        lng FLOAT,
        saved_at DATETIME,
        temperature DECIMAL(5, 2)
    );
    """
    db_client.query_fix(create_table_query)

def insert_weather_data(weather_data):
    insert_query = """
    INSERT INTO weather (bikeable, icon, lat, lng, saved_at, temperature)
    VALUES (?, ?, ?, ?, ?, ?);
    """
    values = (
        weather_data['bikeable'],
        weather_data['icon'],
        weather_data['location']['lat'],
        weather_data['location']['lng'],
        weather_data['saved_at'],
        weather_data['temperature']
    )
    db_client.insert(keys=('bikeable', 'icon', 'lat', 'lng', 'saved_at', 'temperature'), values=values, table='weather')

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
        return None, None

def get_weather(latitude, longitude):
    api_key = os.getenv('WEATHER_API_KEY')
    api_url_base = os.getenv('WEATHER_API_URL', 'https://dataservice.accuweather.com')
    api_url = f'{api_url_base}/locations/v1/cities/geoposition/search'

    params = {
        'apikey': api_key,
        'q': f'{latitude},{longitude}'
    }

    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        location_data_unformatted = response.json()
        location_data = [location_data_unformatted]
        location_key = location_data[0]['Key']
        api_url = f'{api_url_base}/currentconditions/v1/{location_key}'

        params = {
            'apikey': api_key,
        }

        weather_response = requests.get(api_url, params=params)
        return weather_response

    else:
        print("Er gaat duidelijk iets NIET goed")

@app.route('/')
def weather():
    create_weather_table()
    latitude, longitude = get_current_location()

    if latitude is not None and longitude is not None:
        weather_response = get_weather(latitude, longitude)

        if weather_response.status_code == 200:
            weather_data = weather_response.json()[0]

            temperature = weather_data['Temperature']['Metric']['Value']
            icon = weather_data['WeatherText']

            bikeable = temperature > 10

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

            insert_weather_data(response_data)

            return jsonify(response_data)
        else:
            return jsonify({'error': 'Unable to retrieve weather data'})
    else:
        return jsonify({'error': 'Unable to retrieve current location coordinates'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
