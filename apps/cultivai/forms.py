from django import forms


class CropForm(forms.Form):
    N = forms.FloatField(
        label="Nitrógeno (N)",
        min_value=0,
        max_value=140,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0-140',
            'required': 'required'
        }),
        help_text="Nivel de nitrógeno en el suelo (0-140)"
    )
    P = forms.FloatField(
        label="Fósforo (P)",
        min_value=5,
        max_value=145,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '5-145',
            'required': 'required'
        }),
        help_text="Nivel de fósforo en el suelo (5-145)"
    )
    K = forms.FloatField(
        label="Potasio (K)",
        min_value=5,
        max_value=205,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '5-205',
            'required': 'required'
        }),
        help_text="Nivel de potasio en el suelo (5-205)"
    )
    temperature = forms.FloatField(
        label="Temperatura (°C)",
        min_value=8.83,
        max_value=43.7,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '8.83-43.7',
            'required': 'required'
        }),
        help_text="Temperatura promedio en grados Celsius (8.83-43.7)"
    )
    humidity = forms.FloatField(
        label="Humedad (%)",
        min_value=14.3,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '14.3-100',
            'required': 'required'
        }),
        help_text="Nivel de humedad relativa (14.3-100)"
    )
    ph = forms.FloatField(
        label="pH",
        min_value=3.5,
        max_value=9.94,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '3.5-9.94',
            'required': 'required'
        }),
        help_text="Nivel de pH del suelo (3.5-9.94)"
    )
    rainfall = forms.FloatField(
        label="Lluvia (mm)",
        min_value=20.2,
        max_value=299,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '20.2-299',
            'required': 'required'
        }),
        help_text="Precipitación pluvial en milímetros (20.2-299)"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add form-control class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
