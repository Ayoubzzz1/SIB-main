from rest_framework import viewsets
from .models import Client, Commande, ArticleCommande, Fournisseur
from .serializers import ClientSerializer, CommandeSerializer, ArticleCommandeSerializer, FournisseurSerializer
from users_app.permissions import IsCommercialOrAdmin, IsAdminOrReadOnly, CanManageOrders, CanViewOrders, CanManageClients
from rest_framework.permissions import IsAuthenticated
from logs_app.mixins import LoggingMixin

class FournisseurViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Fournisseur.objects.filter(est_actif=True)
    serializer_class = FournisseurSerializer
    permission_classes = [IsCommercialOrAdmin]  # Commerciaux et admins peuvent gérer

    def perform_destroy(self, instance):
        # Soft delete - mark as inactive instead of deleting
        instance.est_actif = False
        instance.save()

class ClientViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [CanManageClients]  # Commerciaux et admins peuvent gérer les clients

    def perform_create(self, serializer):
        serializer.save()

class CommandeViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Commande.objects.all().select_related('id_client', 'cree_par')
    serializer_class = CommandeSerializer
    permission_classes = [CanManageOrders]  # Commerciaux et admins peuvent gérer les commandes

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [CanViewOrders()]  # Magasiniers et Production peuvent voir les commandes
        return [CanManageOrders()]  # Commerciaux et admins peuvent gérer

    def perform_create(self, serializer):
        serializer.save(cree_par=self.request.user.utilisateur)

class ArticleCommandeViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = ArticleCommande.objects.all().select_related('id_commande', 'id_produit')
    serializer_class = ArticleCommandeSerializer
    permission_classes = [CanManageOrders]  # Commerciaux et admins peuvent gérer les articles de commande

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [CanViewOrders()]  # Magasiniers et Production peuvent voir les articles de commande
        return [CanManageOrders()]  # Commerciaux et admins peuvent gérer
