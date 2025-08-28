from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .models import HistoriqueActivite
from .serializers import HistoriqueActiviteSerializer
from users_app.permissions import CanViewLogs

class HistoriqueActiviteViewSet(viewsets.ReadOnlyModelViewSet): # ReadOnlyModelViewSet car les logs ne sont pas modifiables via l'API
    queryset = HistoriqueActivite.objects.all().select_related('id_utilisateur')
    serializer_class = HistoriqueActiviteSerializer
    permission_classes = [CanViewLogs] # Seuls les admins peuvent lire les logs

    @action(detail=False, methods=['get'])
    def test(self, request):
        """Test endpoint to verify the API is working"""
        return Response({
            "message": "Activity logs API is working",
            "user": request.user.username if request.user else "No user",
            "authenticated": request.user.is_authenticated if request.user else False,
            "total_logs": HistoriqueActivite.objects.count()
        })
