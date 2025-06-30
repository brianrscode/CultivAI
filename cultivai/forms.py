from django import forms

class CropForm(forms.Form):
    N = forms.FloatField(label="Nitrogen (N)", widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': '0-140'
    }))

    P = forms.FloatField(label="Phosphorus (P)", widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': '5-145'
    }))

    K = forms.FloatField(label="Potassium (K)", widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': '5-205'
    }))

    temperature = forms.FloatField(label="Temperature (°C)", widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': '8.83-43.7'
    }))

    humidity = forms.FloatField(label="Humidity (%)", widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': '14.3-100'
    }))

    ph = forms.FloatField(label="pH", widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': '3.5-9.94'
    }))

    rainfall = forms.FloatField(label="Rainfall (mm)", widget=forms.NumberInput(attrs={
        'class': 'form-control', 'placeholder': '20.2-299'
    }))
