import requests
import logging
import time

BASE_URL = "https://api.open-meteo.com/v1/forecast"

logger = logging.getLogger(__name__)


def fetch_weather(latitude: float, longitude: float, retries: int = 1) -> dict | None:
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
            print(f"  Request Status: {response.status_code}")
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            print(f"  Timeout on attempt {attempts}/{max_attempts}.")
            logger.warning("Request timed out (attempt %d/%d).", attempts, max_attempts)
            if attempts < max_attempts:
                time.sleep(2)  # brief pause before retry

        except requests.exceptions.HTTPError as e:
            print(f"  HTTP error: {e} — skipping.")
            logger.error("HTTP error %s — skipping this location.", e)
            return None  # non-transient, no point retrying

        except requests.exceptions.RequestException as e:
            print(f"  Network error: {e} — skipping.")
            logger.error("Network error: %s", e)
            return None

    logger.error("All %d attempt(s) failed for (%.4f, %.4f).", max_attempts, latitude, longitude)
    return None


def parse_data(data: dict, city: str) -> list[dict]:
    hourly        = data.get("hourly", {})
    time_steps    = hourly.get("time", [])
    temperature   = hourly.get("temperature_2m", [])
    apparent_temp = hourly.get("apparent_temperature", [])
    humidity      = hourly.get("relativehumidity_2m", [])
    windspeed     = hourly.get("windspeed_10m", [])
    precipitation = hourly.get("precipitation", [])
    cloudcover    = hourly.get("cloudcover", [])

    def safe_get(lst, idx):
        return lst[idx] if idx < len(lst) else None

    records = []
    for i, ts in enumerate(time_steps):
        records.append({
            "city":                   city,
            "time":                   ts,
            "temperature_c":          safe_get(temperature, i),
            "apparent_temperature_c": safe_get(apparent_temp, i),
            "humidity_pct":           safe_get(humidity, i),
            "windspeed_kmh":          safe_get(windspeed, i),
            "precipitation_mm":       safe_get(precipitation, i),
            "cloudcover_pct":         safe_get(cloudcover, i),
        })

    return records