from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CropInputSerializer
from django.conf import settings
from .services.ml_service import CropRecommendationService

ml_service = CropRecommendationService(settings.MODEL_PATH, settings.ENCODER_PATH)

class CropRecommendationView(APIView):
    def post(self, request):
        serializer = CropInputSerializer(data=request.data)
        if not serializer.is_valid():
            # Si el serializer falla, retorna los errores del serializer
            return Response({
                'success': False,
                'message': 'Datos de entrada inválidos',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        result = ml_service.predict_crop(data)

        # Si el modelo retorna error, usa status 400 y un mensaje claro
        if not result.get('success', False):
            return Response({
                'success': False,
                'message': result.get('error', 'Error en la predicción'),
                'errors': result.get('errors', [])
            }, status=status.HTTP_400_BAD_REQUEST)

        # Si todo va bien, retorna el resultado y un mensaje de éxito
        return Response({
            'message': 'Predicción realizada con éxito',
            **result
        }, status=status.HTTP_200_OK)

