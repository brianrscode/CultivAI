import logging
import os
import time
from typing import Dict, List

import numpy as np
import pandas as pd
from joblib import load

logger = logging.getLogger('predictions')

class CropRecommendationService:
    """
    Servicio de recomendaciones de cultivos basado en Machine Learning


    Args:
        model_path (str): Ruta al modelo ML entrenado
        encoder_path (str): Ruta al encoder de etiquetas
    """

    def __init__(self, model_path: str, encoder_path: str):
        self.model = None
        self.label_encoder = None
        self.model_loaded = False
        self.model_version = "1.0"

        # Guardar rutas de modelo y encoder
        self.model_path = model_path
        self.encoder_path = encoder_path

        # Diccionario de traducciones
        self.translations = {
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

        # Cargar modelo al inicializar
        self._load_model()

    def _load_model(self):
        """Carga el modelo y el label encoder desde archivos joblib"""
        try:
            # Usar los paths proporcionados
            model_path = self.model_path
            encoder_path = self.encoder_path

            # Verificar que los archivos existen
            if not os.path.exists(model_path):
                logger.error(f"Modelo no encontrado en: {model_path}")
                return False

            if not os.path.exists(encoder_path):
                logger.error(f"Label encoder no encontrado en: {encoder_path}")
                return False

            # Cargar modelo y encoder
            self.model = load(model_path)
            self.label_encoder = load(encoder_path)
            self.model_loaded = True

            logger.info("Modelo ML cargado exitosamente")
            return True

        except Exception as e:
            logger.error(f"Error cargando modelo ML: {e}")
            self.model_loaded = False
            return False

    def is_model_available(self) -> bool:
        """Verifica si el modelo está disponible para predicciones"""
        return self.model_loaded and self.model is not None and self.label_encoder is not None

    def predict_crop(self, data_received: Dict) -> Dict:
        """
        Realiza predicción de cultivo basada en datos de sensores

        Args:
            data_received (dict): Datos con keys: N, P, K, temperature, humidity, ph, rainfall

        Returns:
            dict: Resultado de la predicción con confianza y recomendaciones
        """

        if not self.is_model_available():
            return {
                'success': False,
                'errors': 'Modelo ML no disponible',
                'predicted_crop': None
            }

        try:
            start_time = time.time()

            # Validar datos de entrada
            validation_result = self._validate_input_data(data_received)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'errors': f"Datos inválidos: {validation_result['errors']}",
                    'predicted_crop': None
                }

            # Preparar datos para el modelo
            input_df = self._prepare_model_input(data_received)

            # Realizar predicción
            prediction = self.model.predict(input_df)[0]
            probabilities = self.model.predict_proba(input_df)[0]

            # Obtener nombre del cultivo
            crop_name = self.label_encoder.inverse_transform([prediction])[0]
            crop_spanish = self.translations.get(crop_name, crop_name)

            # Calcular confianza y top recomendaciones
            confidence = float(np.max(probabilities))
            top_recommendations = self._get_top_recommendations(probabilities)

            # Tiempo de procesamiento
            prediction_time = int((time.time() - start_time) * 1000)

            result = {
                'success': True,
                'predicted_crop': crop_name,
                'predicted_crop_spanish': crop_spanish,
                'confidence_score': confidence,
                'confidence_percentage': round(confidence * 100, 1),
                'confidence_level': self._get_confidence_level(confidence),
                'top_recommendations': top_recommendations,
                'all_probabilities': self._get_all_probabilities(probabilities),
                'model_version': self.model_version,
                'prediction_time_ms': prediction_time,
                'input_data': data_received
            }

            logger.info(f"Predicción exitosa: {crop_spanish} ({confidence:.2%})")
            return result

        except Exception as e:
            logger.error(f"Error en predicción: {e}")
            return {
                'success': False,
                'errors': f'Error interno en predicción: {str(e)}',
                'predicted_crop': None
            }

    def _validate_input_data(self, data: Dict) -> Dict:
        """Valida que los datos de entrada estén completos y en rangos válidos"""

        errors = []
        required_fields = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']

        # Verificar campos requeridos
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f"Campo requerido faltante: {field}")

        if errors:
            return {'valid': False, 'errors': errors}

        # Validar rangos (basados en el dataset original)
        ranges = {
            'N': (0, 140, 'Nitrógeno'),
            'P': (5, 145, 'Fósforo'),
            'K': (5, 205, 'Potasio'),
            'temperature': (8.83, 43.7, 'Temperatura'),
            'humidity': (14.3, 100, 'Humedad'),
            'ph': (3.5, 9.94, 'pH'),
            'rainfall': (0, 299, 'Precipitación')
        }

        for field, (min_val, max_val, name) in ranges.items():
            value = data[field]
            if not isinstance(value, (int, float)):
                errors.append(f"{name} debe ser numérico")
            elif value < min_val or value > max_val:
                errors.append(f"{name}: valor {value} fuera del rango [{min_val}, {max_val}]")

        return {'valid': len(errors) == 0, 'errors': errors}

    def _prepare_model_input(self, data_received: Dict) -> pd.DataFrame:
        """Prepara los datos en el formato esperado por el modelo"""

        input_data = [
            data_received['N'],
            data_received['P'],
            data_received['K'],
            data_received['temperature'],
            data_received['humidity'],
            data_received['ph'],
            data_received['rainfall']
        ]

        columns = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']

        return pd.DataFrame([input_data], columns=columns)

    def _get_top_recommendations(self, probabilities: np.ndarray, top_n: int = 3) -> List[Dict]:
        """Obtiene las top N recomendaciones con sus probabilidades"""

        # Obtener índices ordenados por probabilidad descendente
        top_indices = np.argsort(probabilities)[::-1][:top_n]

        recommendations = []
        for i, idx in enumerate(top_indices):
            crop_name = self.label_encoder.inverse_transform([idx])[0]
            crop_spanish = self.translations.get(crop_name, crop_name)
            probability = float(probabilities[idx])

            recommendations.append({
                'rank': i + 1,
                'crop': crop_name,
                'crop_spanish': crop_spanish,
                'probability': probability,
                'percentage': round(probability * 100, 1)
            })

        return recommendations

    def _get_all_probabilities(self, probabilities: np.ndarray) -> Dict:
        """Convierte todas las probabilidades en un diccionario"""

        all_probs = {}
        for i, prob in enumerate(probabilities):
            crop_name = self.label_encoder.inverse_transform([i])[0]
            all_probs[crop_name] = float(prob)

        return all_probs

    def _get_confidence_level(self, confidence: float) -> str:
        """Categoriza el nivel de confianza"""
        if confidence >= 0.90:
            return 'muy_alta'
        elif confidence >= 0.80:
            return 'alta'
        elif confidence >= 0.60:
            return 'media'
        else:
            return 'baja'

    def get_crop_recommendations_text(self, crop_name: str, data_recived: Dict) -> Dict:
        """
        Genera recomendaciones textuales para el cultivo predicho

        Args:
            crop_name (str): Nombre del cultivo en inglés
            sensor_data (dict): Datos de sensores para análisis

        Returns:
            dict: Recomendaciones textuales
        """

        recommendations = {
            'planting_season': '',
            'irrigation_recommendation': '',
            'fertilization_recommendation': '',
            'pest_control_tips': '',
            'expected_yield': '',
            'growth_duration': '',
            'soil_warnings': '',
            'climate_warnings': ''
        }

        # Base de conocimiento simple para cultivos comunes
        crop_info = {
            'rice': {
                'planting_season': 'Época de lluvias (junio-julio)',
                'irrigation_recommendation': 'Mantener suelo inundado durante crecimiento',
                'fertilization_recommendation': 'Aplicar nitrógeno en 3 etapas',
                'growth_duration': '120-150 días',
                'expected_yield': '4-6 toneladas/hectárea'
            },
            'maize': {
                'planting_season': 'Inicio de temporada de lluvias',
                'irrigation_recommendation': 'Riego regular, evitar encharcamiento',
                'fertilization_recommendation': 'NPK 20-10-10 al momento de siembra',
                'growth_duration': '90-120 días',
                'expected_yield': '3-5 toneladas/hectárea'
            },
            'cotton': {
                'planting_season': 'Abril-mayo',
                'irrigation_recommendation': 'Riego por goteo recomendado',
                'fertilization_recommendation': 'Alto requerimiento de potasio',
                'growth_duration': '180-200 días',
                'expected_yield': '1-2 toneladas/hectárea'
            }
        }

        if crop_name in crop_info:
            recommendations.update(crop_info[crop_name])

        # Advertencias basadas en condiciones actuales
        temp = data_recived.get('temperature', 25)
        humidity = data_recived.get('humidity', 50)
        ph = data_recived.get('ph', 7)

        warnings = []

        if temp > 35:
            warnings.append("Temperatura alta - considerar sombra o riego adicional")
        elif temp < 15:
            warnings.append("Temperatura baja - puede retrasar germinación")

        if humidity > 80:
            warnings.append("Humedad alta - riesgo de enfermedades fúngicas")
        elif humidity < 30:
            warnings.append("Humedad baja - aumentar frecuencia de riego")

        if ph < 6:
            warnings.append("Suelo ácido - considerar aplicar cal")
        elif ph > 8:
            warnings.append("Suelo alcalino - añadir materia orgánica")

        if warnings:
            recommendations['climate_warnings'] = '; '.join(warnings)

        return recommendations
