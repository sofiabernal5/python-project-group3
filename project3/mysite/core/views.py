from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.management import call_command
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST

from .models import AirQualityRecord, Location, City, WeatherRecord
from .forms import AirQualityRecordForm


# ── Home ────────────────────────────────────────────────────────────────────

def home(request):
    total_records = AirQualityRecord.objects.count() + WeatherRecord.objects.count()
    total_locations = Location.objects.count()
    total_cities = City.objects.count()
    
    recent_air_quality = AirQualityRecord.objects.select_related('location').order_by('-date')[:5]
    recent_weather = WeatherRecord.objects.select_related('city').order_by('-date', '-time')[:5]

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