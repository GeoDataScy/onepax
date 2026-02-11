from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes # Keep for status view
from rest_framework.response import Response # Keep for status view
from controle_acesso.permissions import IsSupervisor
from .models import BriefingSession
from .serializers import BriefingSessionSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSupervisor])
def briefing_status(request):
    """Status do módulo Sala de Briefing"""
    return Response({
        'status': 'ok',
        'module': 'sala_briefing',
        'message': 'Módulo Sala de Briefing ativo',
    })

class BriefingListCreateView(generics.ListCreateAPIView):
    queryset = BriefingSession.objects.all()
    serializer_class = BriefingSessionSerializer
    permission_classes = [IsAuthenticated, IsSupervisor]

class BriefingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BriefingSession.objects.all()
    serializer_class = BriefingSessionSerializer
    permission_classes = [IsAuthenticated, IsSupervisor]
