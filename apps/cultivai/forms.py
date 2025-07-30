from django import forms


class CropForm(forms.Form):
    N = forms.FloatField(
        label="Nitrogen (N)",
        min_value=0,
        max_value=140,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0-140'})
    )
    P = forms.FloatField(
        label="Phosphorus (P)",
        min_value=5,
        max_value=145,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '5-145'})
    )
    K = forms.FloatField(
        label="Potassium (K)",
        min_value=5,
        max_value=205,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '5-205'})
    )
    temperature = forms.FloatField(
        label="Temperature (°C)",
        min_value=8.83,
        max_value=43.7,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '8.83-43.7'})
    )
    humidity = forms.FloatField(
        label="Humidity (%)",
        min_value=14.3,
        max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '14.3-100'})
    )
    ph = forms.FloatField(
        label="pH",
        min_value=3.5,
        max_value=9.94,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '3.5-9.94'})
    )
    rainfall = forms.FloatField(
        label="Rainfall (mm)",
        min_value=20.2,
        max_value=299,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '20.2-299'})
    )
