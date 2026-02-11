from rest_framework import serializers
from .models import BriefingSession

class BriefingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BriefingSession
        fields = '__all__'
