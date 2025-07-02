# data_app/serializers.py
from rest_framework import serializers
from .models import Seriada062025, Llaves062025, Forja062025, Maestranza062025

class Seriada062025Serializer(serializers.ModelSerializer):
    class Meta:
        model = Seriada062025
        fields = '__all__'

class Llaves062025Serializer(serializers.ModelSerializer):
    class Meta:
        model = Llaves062025
        fields = '__all__'

class Forja062025Serializer(serializers.ModelSerializer):
    class Meta:
        model = Forja062025
        fields = '__all__'

class Maestranza062025Serializer(serializers.ModelSerializer):
    class Meta:
        model = Maestranza062025
        fields = '__all__'
