import pandas as pd
import plotly.express as px
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from joblib import load

from .forms import CropForm
# from plotly.offline import plot  # Para generar gráficos interactivos en HTML


model = load("./model/crop_recommendation_model.joblib")
label_encoder = load("./model/label_encoder.joblib")
data = pd.read_csv('./static/data/Crop_recommendation.csv')


def index_view(request):
    if request.method != 'POST':
        form = CropForm()
        return render(request, 'index.html', {'form': form})

    form = CropForm(request.POST)
    if not form.is_valid():
        return render(request, 'index.html', {'form': form})

    data = form.cleaned_data
    input_df = pd.DataFrame(
        [[data['N'], data['P'], data['K'], data['temperature'], data['humidity'], data['ph'], data['rainfall']]],
        columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    )

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

    crop = traducciones.get(crop_name, crop_name)
    return render(request, 'index.html', {'form': form, 'crop': crop})


def generar_grafico(y, title):
    fig = px.box(data, x='label', y=y, title=title)
    fig.update_layout(margin={"l": 0, "r": 0, "t": 30, "b": 0}, autosize=True)
    fig_html = fig.to_html(full_html=False)
    return fig_html


def graphics_view(request):
    fig_box_n_html = generar_grafico('N', 'Nivel de Nitrógeno')
    fig_box_p_html = generar_grafico('P', 'Nivel de Fósforo')
    fig_box_k_html = generar_grafico('K', 'Nivel de Potasio')
    fig_box_temperature_html = generar_grafico('temperature', 'Temperatura')
    fig_box_humidity_html = generar_grafico('humidity', 'Nivel de humedad')
    fig_box_ph_html = generar_grafico('ph', 'Nivel de pH ')
    fig_box_rainfall_html = generar_grafico('rainfall', 'Nivel de lluvia')

    # Obtener importancia de las características
    feature_importances = pd.Series(model.feature_importances_, index=data.columns[:-1])
    barra_importancia = px.bar(feature_importances.sort_values(ascending=True), orientation='h', title="Importancia de cada característica")
    barra_importancia.update_layout(
        xaxis_title="Importancia",
        yaxis_title="Característica"
    )
    barra_importancia_html = barra_importancia.to_html(full_html=False)


    context = {
        'fig_box_n': fig_box_n_html,
        'fig_box_p': fig_box_p_html,
        'fig_box_k': fig_box_k_html,
        'fig_box_temperature': fig_box_temperature_html,
        'fig_box_humidity': fig_box_humidity_html,
        'fig_box_ph': fig_box_ph_html,
        'fig_box_rainfall': fig_box_rainfall_html,
        'barra_importancia': barra_importancia_html
    }
    return render(request, 'graficos.html', context)


datos_ambiente_temporal = {}  # Diccionario para almacenar temporalmente los datos

@csrf_exempt
def receive_arduino_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            temperature = data.get('temperature')
            humidity = data.get('humidity')

            if temperature is not None and humidity is not None:
                # Almacenar los datos temporalmente
                datos_ambiente_temporal['temperature'] = temperature
                datos_ambiente_temporal['humidity'] = humidity
                return JsonResponse({
                    'status': 'success',
                    'temperature': temperature,
                    'humidity': humidity
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'Datos incompletos'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

def obtener_ultimos_datos(request):
    """
    Endpoint para obtener los últimos datos de temperatura y humedad
    """
    if 'temperature' in datos_ambiente_temporal and 'humidity' in datos_ambiente_temporal:
        return JsonResponse({
            'temperature': datos_ambiente_temporal['temperature'],
            'humidity': datos_ambiente_temporal['humidity']
        })
    else:
        return JsonResponse({
            'temperature': None,
            'humidity': None
        })