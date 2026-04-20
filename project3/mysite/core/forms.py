from django import forms
from .models import Classification


class ClassificationForm(forms.ModelForm):
    class Meta:
        model = Classification
        fields = [
            'city', 'time', 'temperature_c', 'apparent_temperature_c',
            'humidity_pct', 'windspeed_kmh', 'precipitation_mm',
            'cloudcover_pct', 'source',
        ]
        widgets = {
            'time': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'form-select')
            elif not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-control')
