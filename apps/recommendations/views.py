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
        if serializer.is_valid():
            data = serializer.validated_data
            result = ml_service.predict_crop(data)
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
