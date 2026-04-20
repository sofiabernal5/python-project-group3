from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.dateparse import parse_datetime
import requests
import time

from core.models import City, WeatherRecord

BASE_URL = "https://api.open-meteo.com/v1/forecast"


class Command(BaseCommand):
    help = "Fetch weather data from Open-Meteo API and store in database"

    def fetch_weather(self, latitude, longitude, retries=1):
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": (
                "temperature_2m,apparent_temperature,"
                "relativehumidity_2m,windspeed_10m,"
                "precipitation,cloudcover"
            ),
            "timezone": "America/New_York",
        }

        attempts = 0
        max_attempts = 1 + retries

        while attempts < max_attempts:
            attempts += 1
            try:
                response = requests.get(BASE_URL, params=params, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout:
                self.stdout.write(f"Timeout ({attempts}/{max_attempts})")
                if attempts < max_attempts:
                    time.sleep(2)
            except requests.exceptions.RequestException as e:
                self.stderr.write(f"Error: {e}")
                return None

        return None

    def handle(self, *args, **options):
        cities = City.objects.all()

        for city in cities:
            self.stdout.write(f"\nFetching {city.name}...")
            data = self.fetch_weather(city.latitude, city.longitude)

            if not data:
                self.stderr.write(f"Skipping {city.name}")
                continue

            hourly = data.get("hourly", {})
            times = hourly.get("time", [])

            temps = hourly.get("temperature_2m", [])
            apparent = hourly.get("apparent_temperature", [])
            humidity = hourly.get("relativehumidity_2m", [])
            windspeed = hourly.get("windspeed_10m", [])
            precipitation = hourly.get("precipitation", [])
            cloudcover = hourly.get("cloudcover", [])

            with transaction.atomic():
                for i, ts in enumerate(times[:24]):  # first 24 hours
                    dt = parse_datetime(ts)
                    if not dt:
                        continue

                    WeatherRecord.objects.update_or_create(
                        city=city,
                        date=dt.date(),
                        time =dt.time(),
                        defaults={
                            "temperature": temps[i] if i < len(temps) else None,
                            "apparent_temperature": apparent[i] if i < len(apparent) else None,
                            "humidity": humidity[i] if i < len(humidity) else None,
                            "windspeed": windspeed[i] if i < len(windspeed) else None,
                            "precipitation": precipitation[i] if i < len(precipitation) else None,
                            "cloudcover": cloudcover[i] if i < len(cloudcover) else None,
                            "source": "api",
                        }
                    )

            self.stdout.write(self.style.SUCCESS(f"Saved {city.name}"))