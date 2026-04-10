import requests
import logging
import time

# URL for the Open-Meteo API 
BASE_URL = "https://api.open-meteo.com/v1/forecast"

# Set up logging for this module
logger = logging.getLogger(__name__)
logging.getLogger("api_client").addHandler(logging.NullHandler())  

# List of cities with their coordinates to fetch weather data for
CITIES = [
    {"name": "Tallahassee", "latitude": 30.4383, "longitude": -84.2807},
    {"name": "Jacksonville", "latitude": 30.3322, "longitude": -81.6557},
    {"name": "Orlando",      "latitude": 28.5383, "longitude": -81.3792},
    {"name": "Tampa",        "latitude": 27.9506, "longitude": -82.4572},
    {"name": "Miami",        "latitude": 25.7617, "longitude": -80.1918},
]


def fetch_weather(latitude: float, longitude: float, retries: int = 1) -> dict | None:
    """
    Fetch hourly weather data for a given latitude and longitude from the Open-Meteo API.
    Retries the request up to `retries` times in case of time errors.
    Returns the JSON response as a dictionary, or None if the request fails.
    """
    # Define the parameters for the API request
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
    # Implement a retry mechanism for errors
    attempts = 0
    max_attempts = 1 + retries
    # Loop until we either get a successful response or spend the retries
    while attempts < max_attempts:
        attempts += 1
        # Try to make the API request and handle potential exceptions
        try:
            # Request
            response = requests.get(BASE_URL, params=params, timeout=10)
            # Log the status code for debugging
            print(f"  Request Status: {response.status_code}")
            # Raise an exception for HTTP errors (4xx or 5xx)
            response.raise_for_status()
            # If it gets here, the request was successful
            return response.json()
        except requests.exceptions.Timeout:
            print(f"  Timeout on attempt {attempts}/{max_attempts}.")
            logger.warning("Request timed out (attempt %d/%d).", attempts, max_attempts)
            if attempts < max_attempts:
                time.sleep(2)
        except requests.exceptions.HTTPError as e:
            print(f"  HTTP error: {e} - skipping.")
            logger.error("HTTP error %s - skipping this location.", e)
            return None  
        except requests.exceptions.RequestException as e:
            print(f"  Network error: {e} - skipping.")
            logger.error("Network error: %s", e)
            return None
    # If it runs out of retries, log an error and return None
    logger.error("All %d attempt(s) failed for (%.4f, %.4f).", max_attempts, latitude, longitude)
    return None


def fetch_all_cities(cities: list[dict] = CITIES) -> tuple[list[dict], list[str]]:
    """
    Fetch weather data for all cities in the provided list.
    Returns a tuple of (all_records, failed_cities) 
    """
    # Initialize lists to store successful records and failed city names
    all_records = []
    failed_cities = []
    # Loop through each city and fetch its weather data
    for city in cities:
        print(f"\nFetching weather data for {city['name']}...")
        # Log the city being processed
        logger.info("Processing city: %s", city["name"])
        # Fetch the weather data for the city's coordinates
        raw = fetch_weather(city["latitude"], city["longitude"], retries=1)
        # If no data is returned, log a warning and add the city to the failed list
        if raw is None:
            logger.warning("Skipping %s - no data returned.", city["name"])
            failed_cities.append(city["name"])
            continue
        # Parse the raw data into structured records and add them to the all_records list
        records = parse_data(raw, city["name"])
        all_records.extend(records)
        logger.info("Parsed %d hourly records for %s.", len(records), city["name"])
    return all_records, failed_cities


def parse_data(data: dict, city: str) -> list[dict]:
    """
    Parse the raw API response data into a list of structured records.
    Each record is a dictionary containing the city name, time, and various weather parameters.
    """
    # Extract the hourly data from the API response. If it's missing, log a warning and return an empty list.
    hourly = data.get("hourly", {})
    if not hourly:
        logger.warning("No hourly data found for %s. The API response may be incomplete.", city)
        print(f"  Warning: no hourly data returned for {city}, skipping.")
        return []
    time_steps    = hourly.get("time", [])
    temperature   = hourly.get("temperature_2m", [])
    apparent_temp = hourly.get("apparent_temperature", [])
    humidity      = hourly.get("relativehumidity_2m", [])
    windspeed     = hourly.get("windspeed_10m", [])
    precipitation = hourly.get("precipitation", [])
    cloudcover    = hourly.get("cloudcover", [])

    def safe_get(lst, idx):
        """Helper function to safely get a value from a list by index"""
        return lst[idx] if idx < len(lst) else None

    # Create a list of records by zipping together the time steps and corresponding weather parameters
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