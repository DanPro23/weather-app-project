from django.shortcuts import render, redirect
from django.http import JsonResponse
import datetime
import requests
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from .models import WeatherData

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
        'city': city,
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


def analytics_view(request):
    city_name = request.GET.get('city', '')

    if city_name:
        # Data filtration
        queryset = WeatherData.objects.filter(city__icontains=city_name).order_by('date')
    else:
        queryset = WeatherData.objects.all().order_by('date')

    df = pd.DataFrame.from_records(queryset.values())

    if df.empty:
        context = {
            'error': 'There is no data for analysis',
            'city_name': city_name
        }
        return render(request, 'main/analytics.html', context)

    df['date'] = pd.to_datetime(df['date'])

    grouped = df.groupby('date').agg({
        'min_temp_c': 'mean',
        'max_temp_c': 'mean',
        'avg_humidity': 'mean'
    }).reset_index()

    grouped = grouped.dropna(subset=['max_temp_c'])

    if grouped.empty:
        context = {
            'error': 'No valid temperature data for analysis',
            'city_name': city_name
        }
        return render(request, 'main/analytics.html', context)

    grouped['day_num'] = (grouped['date'] - grouped['date'].min()).dt.days

    model = LinearRegression()
    model.fit(grouped[['day_num']].values, grouped['max_temp_c'].values)

    future_days = np.arange(grouped['day_num'].max() + 1, grouped['day_num'].max() + 6)
    predicted_max_temp = model.predict(future_days.reshape(-1, 1))

    future_dates = pd.date_range(start=grouped['date'].max() + pd.Timedelta(days=1), periods=5)

    forecast_result = pd.DataFrame({
        'date': future_dates,
        'predicted_max_temp': predicted_max_temp
    })

    context = {
        'forecast': forecast_result.to_dict(orient='records'),
        'summary': {
            'avg_max_temp': round(grouped['max_temp_c'].mean(), 2),
            'avg_min_temp': round(grouped['min_temp_c'].mean(), 2),
            'avg_humidity': round(grouped['avg_humidity'].mean(), 2)
        },
        'city_name': city_name
    }

    return render(request, 'main/analytics.html', context)


def weather_chart_data(request, city_name):
    queryset = WeatherData.objects.filter(city__icontains=city_name).order_by('date')

    if not queryset.exists():
        return JsonResponse({'error': f'No data found for city "{city_name}"'}, status=404)

    df = pd.DataFrame.from_records(queryset.values('date', 'min_temp_c', 'max_temp_c'))

    df['date'] = pd.to_datetime(df['date'])

    df = df.dropna(subset=['min_temp_c', 'max_temp_c'])

    if df.empty:
        return JsonResponse({'error': f'No valid temperature data for city "{city_name}"'}, status=404)

    chart_data = {
        'labels': df['date'].dt.strftime('%Y-%m-%d').tolist(),
        'max_temp': df['max_temp_c'].tolist(),
        'min_temp': df['min_temp_c'].tolist(),
    }

    return JsonResponse(chart_data)
