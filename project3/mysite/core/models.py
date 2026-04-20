from django.db import models
from django.core.exceptions import ValidationError


def validate_aqi(value):
    if value is not None and (value < 0 or value > 500):
        raise ValidationError(f"AQI value {value} is out of the valid range (0-500).")


class Location(models.Model):
    address = models.CharField(max_length=255)
    city    = models.CharField(max_length=100)
    county  = models.CharField(max_length=100)
    state   = models.CharField(max_length=100)

    class Meta:
        ordering = ["state", "city"]
        unique_together = ["address", "city", "state"]
        verbose_name = "Monitoring Station"
        verbose_name_plural = "Monitoring Stations"

    def __str__(self):
        return f"{self.address}, {self.city}, {self.state}"


class DataRun(models.Model):
    SOURCE_CHOICES = [
        ("csv", "CSV Import"),
        ("api", "API Fetch"),
    ]

    source          = models.CharField(max_length=10, choices=SOURCE_CHOICES)
    started_at      = models.DateTimeField(auto_now_add=True)
    records_created = models.PositiveIntegerField(default=0)
    records_updated = models.PositiveIntegerField(default=0)
    notes           = models.TextField(blank=True)

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "Data Run"
        verbose_name_plural = "Data Runs"

    def __str__(self):
        return (
            f"{self.get_source_display()} — "
            f"{self.started_at.strftime('%Y-%m-%d %H:%M')} "
            f"({self.records_created} created, {self.records_updated} updated)"
        )


class AirQualityRecord(models.Model):
    SOURCE_CHOICES = [
        ("csv", "CSV Import"),
        ("api", "API Fetch"),
    ]

    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="records")
    data_run = models.ForeignKey(DataRun, on_delete=models.SET_NULL, null=True, blank=True, related_name="records")

    date       = models.DateField()
    source     = models.CharField(max_length=10, choices=SOURCE_CHOICES, default="csv")
    created_at = models.DateTimeField(auto_now_add=True)

    o3_mean          = models.FloatField(null=True, blank=True)
    o3_1st_max_value = models.FloatField(null=True, blank=True)
    o3_1st_max_hour  = models.IntegerField(null=True, blank=True)
    o3_aqi           = models.IntegerField(null=True, blank=True, validators=[validate_aqi])

    co_mean          = models.FloatField(null=True, blank=True)
    co_1st_max_value = models.FloatField(null=True, blank=True)
    co_1st_max_hour  = models.IntegerField(null=True, blank=True)
    co_aqi           = models.IntegerField(null=True, blank=True, validators=[validate_aqi])

    so2_mean          = models.FloatField(null=True, blank=True)
    so2_1st_max_value = models.FloatField(null=True, blank=True)
    so2_1st_max_hour  = models.IntegerField(null=True, blank=True)
    so2_aqi           = models.IntegerField(null=True, blank=True, validators=[validate_aqi])

    no2_mean          = models.FloatField(null=True, blank=True)
    no2_1st_max_value = models.FloatField(null=True, blank=True)
    no2_1st_max_hour  = models.IntegerField(null=True, blank=True)
    no2_aqi           = models.IntegerField(null=True, blank=True, validators=[validate_aqi])

    class Meta:
        ordering = ["-date"]
        unique_together = ["location", "date"]
        verbose_name = "Air Quality Record"
        verbose_name_plural = "Air Quality Records"

    def __str__(self):
        return f"{self.location.city} — {self.date}"

    @property
    def max_aqi(self):
        values = [v for v in [self.o3_aqi, self.co_aqi, self.so2_aqi, self.no2_aqi] if v is not None]
        return max(values) if values else None

    @property
    def dominant_pollutant(self):
        candidates = {"O3": self.o3_aqi, "CO": self.co_aqi, "SO2": self.so2_aqi, "NO2": self.no2_aqi}
        valid = {k: v for k, v in candidates.items() if v is not None}
        return max(valid, key=valid.get) if valid else "N/A"

class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        unique_together = ("name", "latitude", "longitude")
        verbose_name = "City"
        verbose_name_plural = "Cities"

    def __str__(self):
        return f"{self.name}, {self.state}"
    
class WeatherRecord(models.Model):
    SOURCE_CHOICES = [
        ("csv", "CSV Import"),
        ("api", "API Fetch"),
    ]

    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="weather_records")
    date = models.DateField()

    temperature = models.FloatField(null=True, blank=True)
    apparent_temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    windspeed = models.FloatField(null=True, blank=True)
    precipitation = models.FloatField(null=True, blank=True)
    cloudcover = models.FloatField(null=True, blank=True)

    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default="api")

    class Meta:
        ordering = ["-date"]
        unique_together = ("city", "date")
        verbose_name = "Weather Record"
        verbose_name_plural = "Weather Records"

    def __str__(self):
        return f"{self.city.name} — {self.date}"