from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from controle_acesso.permissions import IsSupervisor
from .models import RegistroTransporte
from .serializers import RegistroTransporteSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSupervisor])
def transporte_status(request):
    """Status do módulo Transporte"""
    return Response({
        'status': 'ok',
        'module': 'transporte',
        'message': 'Módulo Transporte ativo',
    })

class TransporteListCreateView(generics.ListCreateAPIView):
    queryset = RegistroTransporte.objects.all()
    serializer_class = RegistroTransporteSerializer
    permission_classes = [IsAuthenticated, IsSupervisor]

class TransporteDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RegistroTransporte.objects.all()
    serializer_class = RegistroTransporteSerializer
    permission_classes = [IsAuthenticated, IsSupervisor]
