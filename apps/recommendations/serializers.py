from rest_framework import serializers


class CropInputSerializer(serializers.Serializer):
    N = serializers.FloatField(min_value=0, max_value=140)
    P = serializers.FloatField(min_value=5, max_value=145)
    K = serializers.FloatField(min_value=5, max_value=205)
    temperature = serializers.FloatField(min_value=8, max_value=44)
    humidity = serializers.FloatField(min_value=14, max_value=100)
    ph = serializers.FloatField(min_value=3.5, max_value=10)
    rainfall = serializers.FloatField(min_value=0, max_value=300)
