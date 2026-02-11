from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer para dados do usuário com role"""
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = ['id']

    def get_role(self, obj):
        try:
            return obj.profile.role
        except Exception:
            return 'apac'


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT customizado que inclui role no token"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Adicionar role ao payload do token
        try:
            token['role'] = user.profile.role
        except Exception:
            token['role'] = 'apac'

        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Adicionar role na resposta de login também
        try:
            data['role'] = self.user.profile.role
        except Exception:
            data['role'] = 'apac'

        data['username'] = self.user.username
        return data
