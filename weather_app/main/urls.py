from django.urls import path
from . import  views

urlpatterns = [
    path('', views.main, name='main'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('weather-chart/<str:city_name>/', views.weather_chart_data, name='weather_chart_data'),
]