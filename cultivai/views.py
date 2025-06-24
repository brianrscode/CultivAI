import pandas as pd
from django.shortcuts import render
from joblib import load

model = load("./model/crop_recommendation_model.joblib")
label_encoder = load("./model/label_encoder.joblib")

def index_view(request):

    if request.method == 'POST':
        # 'N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'
        n = float(request.POST.get('N'))
        p = float(request.POST.get('P'))
        k = float(request.POST.get('K'))
        temperature = float(request.POST.get('temperature'))
        humidity = float(request.POST.get('humidity'))
        ph = float(request.POST.get('ph'))
        rainfall = float(request.POST.get('rainfall'))

        # Crear un DataFrame con nombres de columnas para evitar el warning
        input_df = pd.DataFrame([[
            n, p, k, temperature, humidity, ph, rainfall
        ]], columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])

        # Hacer la predicción
        predicted_class = model.predict(input_df)
        crop_name = label_encoder.inverse_transform(predicted_class)[0]

        traducciones = {
            'apple': 'Manzana',
            'banana': 'Plátano',
            'blackgram': 'Frijol negro',
            'chickpea': 'Garbanzo',
            'coffee': 'Café',
            'coconut': 'Coco',
            'cotton': 'Algodón',
            'grapes': 'Uvas',
            'jute': 'Yute',
            'kidneybeans': 'Frijoles rojos',
            'lentil': 'Lentejas',
            'maize': 'Maíz',
            'mango': 'Mango',
            'mothbeans': 'Frijoles de polilla',
            'mungbean': 'Frijol mungo',
            'muskmelon': 'Melón',
            'orange': 'Naranja',
            'papaya': 'Papaya',
            'pigeonpeas': 'Guisante de paloma',
            'pomegranate': 'Granada',
            'rice': 'Arroz',
            'watermelon': 'Sandía'
        }


        return render(request, 'index.html', {'crop': traducciones[crop_name]})

    return render(request, 'index.html')