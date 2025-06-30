import pandas as pd
from django.shortcuts import render
from joblib import load

import plotly.express as px
# from plotly.offline import plot  # Para generar gráficos interactivos en HTML


model = load("./model/crop_recommendation_model.joblib")
label_encoder = load("./model/label_encoder.joblib")
data = pd.read_csv('./static/data/Crop_recommendation.csv')


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