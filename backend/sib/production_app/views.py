from rest_framework import viewsets
from .models import Production, MatiereProduction, NomenclatureProduits
from .serializers import ProductionSerializer, MatiereProductionSerializer, NomenclatureProduitsSerializer
from users_app.permissions import IsProductionOrAdmin, IsAdminOrReadOnly, CanManageProduction
from rest_framework.permissions import IsAuthenticated
from logs_app.mixins import LoggingMixin

class ProductionViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Production.objects.all().select_related('produit_semi_fini', 'produit_fini', 'cree_par')
    serializer_class = ProductionSerializer
    permission_classes = [CanManageProduction]  # Production workers and Admin can manage

    def perform_create(self, serializer):
        serializer.save()

class MatiereProductionViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = MatiereProduction.objects.all().select_related('id_production', 'id_matiere')
    serializer_class = MatiereProductionSerializer
    permission_classes = [CanManageProduction]  # Production workers and Admin can manage

class NomenclatureProduitsViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = NomenclatureProduits.objects.all()
    serializer_class = NomenclatureProduitsSerializer
    permission_classes = [IsAdminOrReadOnly]  # Only admin can modify, all can view
