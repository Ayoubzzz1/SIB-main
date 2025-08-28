from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Message
from .serializers import MessageSerializer
from users_app.permissions import IsAdmin, IsOwnerOrAdmin
from logs_app.mixins import LoggingMixin

class MessageViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Message.objects.all().select_related('id_expediteur', 'id_destinataire')
    serializer_class = MessageSerializer

    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            # Pour la lecture, mise à jour ou suppression d'un message spécifique
            self.permission_classes = [IsOwnerOrAdmin]
        else:
            # Pour la liste ou la création
            self.permission_classes = [IsAuthenticated] # Tout utilisateur authentifié peut créer/lister
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        # Les utilisateurs peuvent voir leurs messages envoyés et reçus
        if self.request.user.is_authenticated and hasattr(self.request.user, 'utilisateur'):
            # Check if user is admin (superuser, staff, or belongs to Administrateurs group)
            if (self.request.user.is_superuser or 
                self.request.user.is_staff or 
                self.request.user.groups.filter(name='Administrateurs').exists()):
                return Message.objects.all().select_related('id_expediteur', 'id_destinataire')
            
            return Message.objects.filter(
                id_expediteur=self.request.user.utilisateur
            ) | Message.objects.filter(
                id_destinataire=self.request.user.utilisateur
            ).select_related('id_expediteur', 'id_destinataire').distinct()
        return Message.objects.none()
