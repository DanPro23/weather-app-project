from django.shortcuts import render
from .models import WeatherData
import datetime
import requests
import pandas as pd

def about(request):
    return render(request, 'main/about.html')

def main(request):
    API_KEY = open("API_KEY.txt", 'r').read().strip()
    base_url = 'http://api.weatherapi.com/v1/forecast.json?key={}&q={}&days=5&aqi=no&alerts=no'

    if request.method == 'POST':
        city1 = request.POST['city1']
        try:
            weather_data, daily_forecast = fetch_data(city1, API_KEY, base_url)
            save_weather_data(city1, weather_data, daily_forecast)

            context = {
                'weather_data': weather_data,
                'daily_forecast': daily_forecast
            }
        except Exception as e:
            context = {
                'error': str(e)
            }
        return render(request, 'main/main.html', context)

    return render(request, 'main/main.html')

def save_weather_data(city, weather_data, forecast):
    # --- Current weather ---
    WeatherData.objects.update_or_create(
        city=city,
        date=datetime.date.today(),
        defaults={
            'temperature_c': weather_data['temperature'],
            'description': weather_data['description'],
            'icon': weather_data['icon'],
            'humidity': weather_data['humidity'],
        }
    )

    # --- Forecast data ---
    for day, item in enumerate(forecast):
        forecast_date = datetime.date.today() + datetime.timedelta(days=day)
        WeatherData.objects.update_or_create(
            city=city,
            date=forecast_date,
            defaults={
                'min_temp_c': item['min_temp'],
                'max_temp_c': item['max_temp'],
                'avg_humidity': item['humidity'],
                'description': item['description'],
                'icon': item['icon'],
                'day_of_week': item['day']
            }
        )

def fetch_data(city, api_key, base_url):
    url = base_url.format(api_key, city)
    response = requests.get(url)
    data = response.json()

    if 'error' in data:
        raise Exception(data['error']['message'])

    weather_data = {
        'city': data['location']['name'],
        'temperature': data['current']['temp_c'],
        'humidity': data['current'].get('humidity'),
        'description': data['current']['condition']['text'],
        'icon': data['current']['condition']['icon']
    }

    daily_forecasts = []
    for forecast_day in data['forecast']['forecastday']:
        day_data = forecast_day['day']
        date = datetime.datetime.strptime(forecast_day['date'], '%Y-%m-%d')
        daily_forecasts.append({
            'day': date.strftime('%A'),
            'min_temp': day_data['mintemp_c'],
            'max_temp': day_data['maxtemp_c'],
            'humidity': day_data.get('avghumidity'),
            'description': day_data['condition']['text'],
            'icon': day_data['condition']['icon']
        })

    return weather_data, daily_forecasts

def analytics_view():
    select_data = WeatherData.objects.all().values()
    data_frame1 = pd.DataFrame(select_data)