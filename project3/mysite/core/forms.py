from django import forms
from .models import AirQualityRecord, WeatherRecord


class AirQualityRecordForm(forms.ModelForm):
    class Meta:
        model  = AirQualityRecord
        fields = [
            'location', 'date', 'source',
            'o3_mean',  'o3_aqi',
            'co_mean',  'co_aqi',
            'so2_mean', 'so2_aqi',
            'no2_mean', 'no2_aqi',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.Select):
                widget.attrs.setdefault('class', 'form-select')
            elif not isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', 'form-control')

class WeatherRecordForm(forms.ModelForm):
    class Meta:
        model = WeatherRecord
        fields = [
            'city',
            'date',
            'time',
            'temperature',
            'apparent_temperature',
            'humidity',
            'windspeed',
            'precipitation',
            'cloudcover',
            'source',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            widget = field.widget

            if isinstance(widget, forms.Select):
                widget.attrs.setdefault('class', 'form-select')
            elif not isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', 'form-control')