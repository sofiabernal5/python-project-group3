from django.contrib import admin, messages
from django.core.management import call_command
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from .models import Location, DataRun, AirQualityRecord, WeatherRecord, City


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display  = ("city", "county", "state", "address")
    list_filter   = ("state", "county")
    search_fields = ("city", "state", "address")
    ordering      = ("state", "city")
    fields = ("address", "city", "county", "state")


@admin.register(DataRun)
class DataRunAdmin(admin.ModelAdmin):
    list_display    = ("source", "started_at", "records_created", "records_updated")
    list_filter     = ("source",)
    readonly_fields = ("started_at",)
    ordering        = ("-started_at",)


@admin.register(AirQualityRecord)
class AirQualityRecordAdmin(admin.ModelAdmin):
    list_display    = ("date", "location", "o3_aqi", "co_aqi", "so2_aqi", "no2_aqi", "source")
    list_filter     = ("source", "location__state", "location__city")
    search_fields   = ("location__city", "location__state", "location__address")
    date_hierarchy  = "date"
    ordering        = ("-date",)
    readonly_fields = ("created_at",)

    fieldsets = (
        ("Record Info", {
            "fields": ("location", "date", "source", "data_run", "created_at"),
        }),
        ("Ozone (O3)", {
            "fields": ("o3_mean", "o3_1st_max_value", "o3_1st_max_hour", "o3_aqi"),
            "classes": ("collapse",),
        }),
        ("Carbon Monoxide (CO)", {
            "fields": ("co_mean", "co_1st_max_value", "co_1st_max_hour", "co_aqi"),
            "classes": ("collapse",),
        }),
        ("Sulphur Dioxide (SO2)", {
            "fields": ("so2_mean", "so2_1st_max_value", "so2_1st_max_hour", "so2_aqi"),
            "classes": ("collapse",),
        }),
        ("Nitrogen Dioxide (NO2)", {
            "fields": ("no2_mean", "no2_1st_max_value", "no2_1st_max_hour", "no2_aqi"),
            "classes": ("collapse",),
        }),
    )

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "latitude", "longitude")
    search_fields = ("name",)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("fetch-weather/", self.admin_site.admin_view(self.fetch_weather))
        ]
        return custom_urls + urls

    def fetch_weather(self, request):
        call_command("fetch_data")
        self.message_user(request, "Weather data fetched successfully.")
        return redirect("..")
    
@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    list_display = (
        "city",
        "date",
        "time",
        "temperature",
        "apparent_temperature",
        "humidity",
        "windspeed",
        "precipitation",
        "cloudcover",
        "source",
    )

    list_filter = ("city", "date", "time")
    search_fields = ("city__name",)

    @admin.display(description="City")
    def city_name(self, obj):
        return obj.city.name
    
    