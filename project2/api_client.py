import requests
import logging
import time

BASE_URL = "https://api.open-meteo.com/v1/forecast"

logger = logging.getLogger(__name__)

CITIES = [
    {"name": "Tallahassee", "latitude": 30.4383, "longitude": -84.2807},
    {"name": "Jacksonville", "latitude": 30.3322, "longitude": -81.6557},
    {"name": "Orlando",      "latitude": 28.5383, "longitude": -81.3792},
    {"name": "Tampa",        "latitude": 27.9506, "longitude": -82.4572},
    {"name": "Miami",        "latitude": 25.7617, "longitude": -80.1918},
]


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


def fetch_all_cities(cities: list[dict] = CITIES) -> tuple[list[dict], list[str]]:
    # Loop over each city (repeated API calls) and aggregate results
    all_records = []
    failed_cities = []

    for city in cities:
        print(f"\nFetching weather data for {city['name']}...")
        logger.info("Processing city: %s", city["name"])

        raw = fetch_weather(city["latitude"], city["longitude"], retries=1)

        if raw is None:
            logger.warning("Skipping %s — no data returned.", city["name"])
            failed_cities.append(city["name"])
            continue

        records = parse_data(raw, city["name"])
        all_records.extend(records)
        logger.info("Parsed %d hourly records for %s.", len(records), city["name"])

    return all_records, failed_cities


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
