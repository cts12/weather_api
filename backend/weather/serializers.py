from rest_framework import serializers


class WeatherSerializer(serializers.Serializer):
    min_humid = serializers.IntegerField(required=True)
    median_humid = serializers.IntegerField(required=True)
    max_humid = serializers.IntegerField(required=True)
    mean_humid = serializers.IntegerField(required=True)

    
    min_temp = serializers.FloatField(required=True)
    median_temp = serializers.FloatField(required=True)
    max_temp = serializers.FloatField(required=True)
    mean_temp = serializers.FloatField(required=True)
