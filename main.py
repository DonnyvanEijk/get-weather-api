import requests
from datetime import datetime
city = input('Give the location of the area u want to check: ')


api_key = 'cHpmNfIS7IBvw5tIuJ3OXK3Uw5p1sUFt'

def get_weather(city):

    location_key = get_location_key(city)

    if location_key is not None:

        api_url = f'http://dataservice.accuweather.com/currentconditions/v1/{location_key}'


        params = {
            'apikey': api_key,
        }


        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            weather_data = response.json()[0]


            temperature_fahrenheit = weather_data.get('Temperature', {}).get('Imperial', {}).get('Value')


            temperature_celsius = (temperature_fahrenheit - 32) * 5/9

            icon = weather_data.get('WeatherIcon')
            if temperature_celsius >= 10:
                is_bikeable = True
            else:
                is_bikeable = False

            saved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


            response_data = {
                "temperature": temperature_celsius,  # Use Celsius if preferred
                "icon": icon,
                "bikeable": is_bikeable,
                "location": {
                "city": city
                },
                "saved_at": saved_at
            }

            return response_data
        else:
            return {'error': 'Unable to fetch weather data'}
    else:
        return {'error': 'Location key not found'}

def get_location_key(city):

    location_api_url = 'http://dataservice.accuweather.com/locations/v1/cities/search'


    params = {
        'apikey': api_key,
        'q': city,
    }


    response = requests.get(location_api_url, params=params)

    if response.status_code == 200:
        location_data = response.json()
        if location_data:

            location_key = location_data[0]['Key']
            return location_key
        else:
            return None
    else:
        return None


weather_data = get_weather(city)
print(weather_data)
