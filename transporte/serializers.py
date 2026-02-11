from rest_framework import serializers
from .models import RegistroTransporte

class RegistroTransporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroTransporte
        fields = '__all__'
