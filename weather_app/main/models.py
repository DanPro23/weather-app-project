from django.db import models

class WeatherData(models.Model):
    # --- Main fields ---
    city = models.CharField("City", max_length=100)
    date = models.DateField("Date")
    icon = models.CharField("Weather Icon URL", max_length=255)
    description = models.TextField("Weather description")

    # --- For current weather ---
    temperature_c = models.FloatField("Temperature (°C)", null=True, blank=True)
    feelslike_c = models.FloatField("Feels Like (°C)", null=True, blank=True)
    humidity = models.IntegerField("Humidity (%)", null=True, blank=True)
    pressure_mb = models.FloatField("Pressure (mb)", null=True, blank=True)
    wind_kph = models.FloatField("Wind Speed (kph)", null=True, blank=True)
    wind_dir = models.CharField("Wind Direction", max_length=15, null=True, blank=True)
    vis_km = models.FloatField("Visibility (km)", null=True, blank=True)
    clouds = models.IntegerField("Cloud Cover (%)", null=True, blank=True)

    # --- For weather forecasting ---
    min_temp_c = models.FloatField("Min Temperature (°C)", null=True, blank=True)
    max_temp_c = models.FloatField("Max Temperature (°C)", null=True, blank=True)
    avg_humidity = models.IntegerField("Average Humidity (%)", null=True, blank=True)
    avg_vis_km = models.FloatField("Average Visibility (km)", null=True, blank=True)
    day_of_week = models.CharField("Day of Week", max_length=20, null=True, blank=True)

    # --- Other fields ---
    timestamp = models.DateTimeField("Data Collection Time", auto_now_add=True)

    class Meta:
        verbose_name = 'Weather Data Record'
        verbose_name_plural = 'Weather Data Records'
        ordering = ['-date', 'city']
        unique_together = ('city', 'date',)

    def __str__(self):
        if self.min_temp_c is not None and self.max_temp_c is not None:
            return f"{self.city} - {self.date} ({self.day_of_week}) - {self.min_temp_c}°C to {self.max_temp_c}°C"
        elif self.temperature_c is not None:
            return f"{self.city} - {self.date} (Current) - {self.temperature_c}°C"
        return f"{self.city} - {self.date}"