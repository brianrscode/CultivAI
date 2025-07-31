import pandas as pd
import plotly.express as px
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .forms import CropForm

from django.conf import settings
from ..recommendations.services.ml_service import CropRecommendationService


ml_service = CropRecommendationService(settings.MODEL_PATH, settings.ENCODER_PATH)
model = ml_service.model
label_encoder = ml_service.label_encoder
data = pd.read_csv('./static/data/Crop_recommendation.csv')


def index_view(request):
    if request.method != 'POST':
        form = CropForm()
        return render(request, 'index.html', {'form': form})

    form = CropForm(request.POST)
    if not form.is_valid():
        return render(request, 'index.html', {'form': form})

    return render(request, 'index.html', {'form': form})


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

@csrf_exempt
def crop_recommendation(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        # Obtener datos del cuerpo de la petición
        data = json.loads(request.body)

        # Validar que todos los campos requeridos estén presentes
        required_fields = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        if not all(field in data for field in required_fields):
            return JsonResponse({'error': 'Faltan campos requeridos'}, status=400)

        # Convertir los datos al formato esperado por el modelo
        input_data = {
            'N': float(data['N']),
            'P': float(data['P']),
            'K': float(data['K']),
            'temperature': float(data['temperature']),
            'humidity': float(data['humidity']),
            'ph': float(data['ph']),
            'rainfall': float(data['rainfall'])
        }

        # Obtener la predicción del modelo
        prediction_result = ml_service.predict_crop(input_data)

        # Formatear la respuesta
        response_data = {
            'success': True,
            'predicted_crop': prediction_result.get('crop', ''),
            'predicted_crop_spanish': prediction_result.get('crop_spanish', ''),
            'confidence_percentage': prediction_result.get('confidence', 0) * 100,
            'confidence_level': get_confidence_level(prediction_result.get('confidence', 0) * 100),
            'model_version': '1.0.0',  # Reemplaza con la versión real de tu modelo
            'input_data': input_data,
            'top_recommendations': prediction_result.get('top_recommendations', [])
        }

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Formato JSON inválido'}, status=400)
    except ValueError as e:
        return JsonResponse({'error': f'Error en los datos: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error interno del servidor: {str(e)}'}, status=500)

def get_confidence_level(percentage):
    """Devuelve el nivel de confianza basado en el porcentaje"""
    if percentage >= 80:
        return 'Muy alta'
    elif percentage >= 60:
        return 'Alta'
    elif percentage >= 40:
        return 'Media'
    else:
        return 'Baja'