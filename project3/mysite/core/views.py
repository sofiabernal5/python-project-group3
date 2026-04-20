from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages

from .models import AirQualityRecord, Location
from .forms import AirQualityRecordForm


# ── Home ────────────────────────────────────────────────────────────────────

def home(request):
    total_records   = AirQualityRecord.objects.count()
    total_locations = Location.objects.count()
    recent          = AirQualityRecord.objects.select_related('location').order_by('-date')[:5]

    context = {
        'total_records':   total_records,
        'total_locations': total_locations,
        'recent':          recent,
    }
    return render(request, 'core/home.html', context)


# ── List (paginated) ────────────────────────────────────────────────────────

def record_list(request):
    qs        = AirQualityRecord.objects.select_related('location').order_by('-date')
    paginator = Paginator(qs, 20)                          # 20 per page
    page_num  = request.GET.get('page', 1)
    page_obj  = paginator.get_page(page_num)

    return render(request, 'core/list.html', {'page_obj': page_obj})


# ── Detail ──────────────────────────────────────────────────────────────────

def record_detail(request, pk):
    record = get_object_or_404(AirQualityRecord.objects.select_related('location'), pk=pk)
    return render(request, 'core/detail.html', {'record': record})


# ── Create ──────────────────────────────────────────────────────────────────

def record_create(request):
    if request.method == 'POST':
        form = AirQualityRecordForm(request.POST)
        if form.is_valid():
            record = form.save()
            messages.success(request, 'Record created successfully.')
            return redirect('core:record_detail', pk=record.pk)
    else:
        form = AirQualityRecordForm()

    return render(request, 'core/form.html', {'form': form, 'action': 'Create'})


# ── Update ──────────────────────────────────────────────────────────────────

def record_update(request, pk):
    record = get_object_or_404(AirQualityRecord, pk=pk)

    if request.method == 'POST':
        form = AirQualityRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Record updated successfully.')
            return redirect('core:record_detail', pk=record.pk)
    else:
        form = AirQualityRecordForm(instance=record)

    return render(request, 'core/form.html', {
        'form':   form,
        'action': 'Update',
        'record': record,
    })


# ── Delete ──────────────────────────────────────────────────────────────────

def record_delete(request, pk):
    record = get_object_or_404(AirQualityRecord, pk=pk)

    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Record deleted.')
        return redirect('core:record_list')

    return render(request, 'core/confirm_delete.html', {'record': record})