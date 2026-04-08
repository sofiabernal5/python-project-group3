import requests

BASE_URL = "https://api.open-meteo.com/v1/forecast"

def fetch_weather(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,apparent_temperature,relativehumidity_2m,windspeed_10m,precipitation,cloudcover",
        "timezone": "America/New_York",
    }
    
    response = requests.get(BASE_URL, params=params, timeout=10)
    print(f"Request Status: {response.status_code}")
    
    return response.json() # return response as JSON 

def parse_data(data, city):
    # Extract relevant hourly data
    hourly = data.get("hourly", {})
    time = hourly.get("time", [])
    temperature = hourly.get("temperature_2m", [])
    apparent_temperature = hourly.get("apparent_temperature", [])
    humidity = hourly.get("relativehumidity_2m", [])
    windspeed = hourly.get("windspeed_10m", [])
    precipitation = hourly.get("precipitation", [])
    cloudcover = hourly.get("cloudcover", [])
    # Create list of records for each hourly data point
    records = []
    for i in range(len(time)):
        record = {
            "city": city,
            "time": time[i] if i < len(time) else None,
            "temperature": temperature[i] if i < len(temperature) else None,
            "apparent_temperature": apparent_temperature[i] if i < len(apparent_temperature) else None,
            "humidity": humidity[i] if i < len(humidity) else None,
            "windspeed": windspeed[i] if i < len(windspeed) else None,
            "precipitation": precipitation[i] if i < len(precipitation) else None,
            "cloudcover": cloudcover[i] if i < len(cloudcover) else None,
        }
        records.append(record)
    return records

def main():
    cities = [
        {"name": "Tallahassee", "latitude": 30.4383, "longitude": -84.2807},
        {"name": "Jacksonville", "latitude": 30.3322, "longitude": -81.6557},
        {"name": "Orlando", "latitude": 28.5383, "longitude": -81.3792},
        {"name": "Tampa", "latitude": 27.9506, "longitude": -82.4572},
        {"name": "Miami", "latitude": 25.7617, "longitude": -80.1918}
    ]
    
    all_weather_data = []
    for city in cities:
        print(f"Fetching weather data for {city['name']}...")
        data = fetch_weather(city["latitude"], city["longitude"]) # fetch weather data for the city
        city_records = parse_data(data, city["name"]) # parse the data into structured records
        all_weather_data.extend(city_records) # add city records to the overall list
    
    print("\nSample records:")
    for record in all_weather_data[:5]: # print the first 5 records as a sample
        print(record)
        
    print(f"\nTotal records collected: {len(all_weather_data)}")
    
if __name__ == "__main__":
    main()
        
    
    
    