from rest_framework import serializers
from .models import Embarque, Desembarque

class EmbarqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Embarque
        fields = '__all__'

class DesembarqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Desembarque
        fields = '__all__'
