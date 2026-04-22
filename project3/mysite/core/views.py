import json

import pandas as pd

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.management import call_command
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST

from .models import AirQualityRecord, Location, City, WeatherRecord
from .forms import AirQualityRecordForm, WeatherRecordForm, CityForm


# ── Home ────────────────────────────────────────────────────────────────────

def home(request):
    total_records = AirQualityRecord.objects.count() + WeatherRecord.objects.count()
    total_locations = Location.objects.count()
    total_cities = City.objects.count()
    
    recent_air_quality = AirQualityRecord.objects.select_related('location').order_by('-date')[:5]
    recent_weather = WeatherRecord.objects.select_related('city').order_by('-date', '-time')[:7]

    context = {
        'total_records':   total_records,
        'total_locations': total_locations,
        'total_cities':    total_cities,
        'recent_air_quality': recent_air_quality,
        'recent_weather': recent_weather,
    }
    return render(request, 'core/home.html', context)


# ── Air Quality List (paginated) ────────────────────────────────────────────────────────

def air_quality_list(request):
    qs        = AirQualityRecord.objects.select_related('location').order_by('-date')
    paginator = Paginator(qs, 20)                          # 20 per page
    page_num  = request.GET.get('page', 1)
    page_obj  = paginator.get_page(page_num)

    return render(request, 'core/list.html', {'page_obj': page_obj})


# ── Air Quality Detail ──────────────────────────────────────────────────────────────────

def air_quality_detail(request, pk):
    record = get_object_or_404(AirQualityRecord.objects.select_related('location'), pk=pk)
    return render(request, 'core/detail.html', {'record': record})


# ── Air Quality Create ──────────────────────────────────────────────────────────────────

def air_quality_create(request):
    if request.method == 'POST':
        form = AirQualityRecordForm(request.POST)
        if form.is_valid():
            record = form.save()
            messages.success(request, 'Record created successfully.')
            return redirect('core:air_quality_detail', pk=record.pk)
    else:
        form = AirQualityRecordForm()

    return render(request, 'core/form.html', {'form': form, 'action': 'Create'})


# ── Air Quality Update ──────────────────────────────────────────────────────────────────

def air_quality_update(request, pk):
    record = get_object_or_404(AirQualityRecord, pk=pk)

    if request.method == 'POST':
        form = AirQualityRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Record updated successfully.')
            return redirect('core:air_quality_detail', pk=record.pk)
    else:
        form = AirQualityRecordForm(instance=record)

    return render(request, 'core/form.html', {
        'form':   form,
        'action': 'Update',
        'record': record,
    })


# ── Air Quality Delete ──────────────────────────────────────────────────────────────────

def air_quality_delete(request, pk):
    record = get_object_or_404(AirQualityRecord, pk=pk)

    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Record deleted.')
        return redirect('core:air_quality_list')

    return render(request, 'core/confirm_delete.html', {'record': record})

# Fetch Weather Data ─────────────────────────────────────────────────────────────────────

@staff_member_required
@require_POST
def fetch_weather_data(request):
    try:
        call_command("fetch_data")
        messages.success(request, "Weather data fetched successfully.")
    except Exception as e:
        messages.error(request, f"Fetch failed: {e}")
    return redirect("core:home")

# ── Weather List (paginated) ────────────────────────────────────────────────────────

def weather_list(request):
    qs = WeatherRecord.objects.select_related('city').order_by('-date', '-time')
    paginator = Paginator(qs, 20)                          # 20 per page
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)

    return render(request, 'core/weather_list.html', {'page_obj': page_obj})

# ── Weather Detail ──────────────────────────────────────────────────────────────────

def weather_detail(request, pk):
    record = get_object_or_404(WeatherRecord.objects.select_related('city'), pk=pk)
    return render(request, 'core/weather_detail.html', {'record': record})

# ── Weather Update ───────────────────────────────────────────────────────

def weather_update(request, pk):
    record = get_object_or_404(WeatherRecord, pk=pk)

    if request.method == 'POST':
        form = WeatherRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Weather record updated successfully.')
            return redirect('core:weather_detail', pk=record.pk)
    else:
        form = WeatherRecordForm(instance=record)

    return render(request, 'core/weather_form.html', {
        'form': form,
        'action': 'Update',
        'record': record,
    })


# ── Weather Delete ──────────────────────────────────────────────────────────────────

def weather_delete(request, pk):
    record = get_object_or_404(WeatherRecord, pk=pk)

    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Record deleted.')
        return redirect('core:weather_list')

    return render(request, 'core/confirm_weather_delete.html', {'record': record})

def fetch_page(request):
    cities = City.objects.all()
    paginator = Paginator(cities, 10)                          # 10 per page
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)

    return render(request, 'core/fetch_page.html', {'page_obj': page_obj})

# ── City Create ───────────────────────────────────────────────────────

def city_create(request):
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "City added successfully.")
            return redirect('core:fetch_page')
    else:
        form = CityForm()

    return render(request, 'core/city_form.html', {
        'form': form,
        'action': 'Add'
    })
    
# ── City Update ───────────────────────────────────────────────────────

def city_update(request, pk):
    city = get_object_or_404(City, pk=pk)

    if request.method == 'POST':
        form = CityForm(request.POST, instance=city)
        if form.is_valid():
            form.save()
            messages.success(request, 'City updated successfully.')
            return redirect('core:fetch_page')
    else:
        form = CityForm(instance=city)

    return render(request, 'core/city_form.html', {
        'form': form,
        'action': 'Update',
        'record': city,
    })


# ── City Delete ───────────────────────────────────────────────────────

def city_delete(request, pk):
    city = get_object_or_404(City, pk=pk)

    if request.method == 'POST':
        city.delete()
        messages.success(request, 'City deleted successfully.')
        return redirect('core:fetch_page')

    return render(request, 'core/confirm_city_delete.html', {'record': city})

# ── City Detail ───────────────────────────────────────────────────────

def city_detail(request, pk):
    city = get_object_or_404(City, pk=pk)
    return render(request, 'core/city_detail.html', {'record': city})

def analytics(request):
    aqi_fields = ['o3_aqi', 'co_aqi', 'so2_aqi', 'no2_aqi']

    records = AirQualityRecord.objects.select_related('location').values(
        'date',
        'location__city',
        'location__state',
        'o3_aqi',
        'co_aqi',
        'so2_aqi',
        'no2_aqi',
    )
    df = pd.DataFrame(list(records))

    if df.empty:
        context = {
            'total_records': 0,
            'total_states': 0,
            'top_state': 'N/A',
            'top_pollutant': 'N/A',
            'monthly_trend_json': json.dumps({'labels': [], 'values': []}),
            'state_summary_json': json.dumps({'labels': [], 'values': []}),
            'pollutant_mix_json': json.dumps({'labels': [], 'values': []}),
            'category_mix_json': json.dumps({'labels': [], 'values': []}),
            'aqi_summary_rows': [],
        }
        return render(request, 'core/analytics.html', context)

    df = df.rename(columns={'location__city': 'city', 'location__state': 'state'})
    df['date'] = pd.to_datetime(df['date'])
    df[aqi_fields] = df[aqi_fields].apply(pd.to_numeric, errors='coerce')
    df['max_aqi'] = df[aqi_fields].max(axis=1)
    df['year_month'] = df['date'].dt.to_period('M').astype(str)

    monthly_trend = (
        df.groupby('year_month')['max_aqi']
        .mean()
        .sort_index()
        .round(1)
    )

    state_summary = (
        df.groupby('state')['max_aqi']
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .round(1)
    )

    def dominant_pollutant(row):
        values = {field: row[field] for field in aqi_fields if pd.notna(row[field])}
        if not values:
            return None
        return max(values, key=values.get)

    df['dominant_pollutant'] = df.apply(dominant_pollutant, axis=1)
    pollutant_labels = {
        'o3_aqi': 'O3',
        'co_aqi': 'CO',
        'so2_aqi': 'SO2',
        'no2_aqi': 'NO2',
    }
    pollutant_mix = (
        df['dominant_pollutant']
        .dropna()
        .map(pollutant_labels)
        .value_counts()
    )

    def aqi_category(value):
        if pd.isna(value):
            return None
        if value <= 50:
            return 'Good'
        if value <= 100:
            return 'Moderate'
        if value <= 150:
            return 'Unhealthy for Sensitive Groups'
        if value <= 200:
            return 'Unhealthy'
        if value <= 300:
            return 'Very Unhealthy'
        return 'Hazardous'

    df['aqi_category'] = df['max_aqi'].apply(aqi_category)
    category_mix = df['aqi_category'].dropna().value_counts()

    summary = (
        df[aqi_fields]
        .agg(['count', 'mean', 'min', 'max'])
        .round(1)
        .T
        .reset_index()
        .rename(columns={'index': 'metric'})
    )

    top_pollutant_key = pollutant_mix.idxmax() if not pollutant_mix.empty else 'N/A'
    top_state = state_summary.idxmax() if not state_summary.empty else 'N/A'

    context = {
        'total_records': len(df),
        'total_states': df['state'].nunique(),
        'top_state': top_state,
        'top_pollutant': top_pollutant_key,
        'monthly_trend_json': json.dumps({
            'labels': monthly_trend.index.tolist(),
            'values': monthly_trend.values.tolist(),
        }),
        'state_summary_json': json.dumps({
            'labels': state_summary.index.tolist(),
            'values': state_summary.values.tolist(),
        }),
        'pollutant_mix_json': json.dumps({
            'labels': pollutant_mix.index.tolist(),
            'values': pollutant_mix.values.tolist(),
        }),
        'category_mix_json': json.dumps({
            'labels': category_mix.index.tolist(),
            'values': category_mix.values.tolist(),
        }),
        'aqi_summary_rows': summary.to_dict(orient='records'),
    }
    return render(request, 'core/analytics.html', context)