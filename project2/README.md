# Automated Weather Data Pipeline

**Group members:**
1. Ashley Oliveira Andrade (ARO22B)
2. Felipe Ubeid (FT23)
3. Sofia Bernal (SB22I)
4. Aidan Thompson (AMT22M)

This pipeline collects hourly weather data for five Florida cities using the Open-Meteo API. It runs on demand (or on a schedule) and appends new results to a local CSV file and SQLite database each run, building up a historical record over time.

**API documentation:** https://open-meteo.com/en/docs

---

## Data pipeline goals

1. Fetch hourly weather data (temperature, humidity, wind speed, precipitation, cloud cover) for 5 cities per run.
2. Accumulate results across runs by appending new rows to `data/processed/weather_data.csv` and `data/processed/weather_data.db`.
3. Handle API failures. Failed cities are skipped and logged without crashing the pipeline.
4. Write all run activity and errors to `logs/pipeline.log` for later review.
5. Support running for a specific subset of cities via command-line arguments.

---

## API justification

**Why Open-Meteo:** It provides free, no-auth access to high-resolution weather forecasts and is well-suited for accumulating daily data across multiple locations.

**Constraints:**
- No API key required.
- Rate limits are generous for personal/educational use (no hard limit documented for low-frequency requests).
- No pagination. Each request returns up to 7 days of hourly data for one location. Multiple calls are made by looping over cities.

---

## SQLite schema

Table name: `weather`

| Column | Type | Description |
|---|---|---|
| city | TEXT | City name |
| time | TEXT | ISO 8601 timestamp |
| temperature_c | REAL | Air temperature (Celsius) |
| apparent_temperature_c | REAL | Feels-like temperature (Celsius) |
| humidity_pct | REAL | Relative humidity (%) |
| windspeed_kmh | REAL | Wind speed at 10m (km/h) |
| precipitation_mm | REAL | Precipitation (mm) |
| cloudcover_pct | REAL | Cloud cover (%) |

---

## How to run

**Run for all cities:**
```
python src/pipeline.py
```

**Run for specific cities:**
```
python src/pipeline.py --cities Tampa Miami Orlando
```

**Available cities:** Tallahassee, Jacksonville, Orlando, Tampa, Miami

**Example output:**
```
Fetching weather data for Tampa...
  Request Status: 200

Fetching weather data for Miami...
  Request Status: 200

--------------------------------------------------
Cities processed : 2/2
Total records    : 336
Saving data...
  CSV saved to data/processed/weather_data.csv (336 rows appended)
  SQLite saved to data/processed/weather_data.db (table: weather, 336 rows appended)
```

Logs are written to `logs/pipeline.log`.

---

## Scheduling (optional)

To run this pipeline automatically every day at 6am, add the following line to your crontab (`crontab -e`):

```
0 6 * * * cd /path/to/project2 && python src/pipeline.py >> logs/cron.log 2>&1
```

On Windows, use the included `run_pipeline.bat` or adapt it:
```bat
@echo off
cd /d C:\path\to\project2
python src\pipeline.py >> logs\cron.log 2>&1
```
