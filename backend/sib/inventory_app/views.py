from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from .models import MatierePremiere, ProduitSemiFini, ProduitFini, Stock, MouvementStock
from .serializers import (
    MatierePremiereSerializer, ProduitSemiFiniSerializer, ProduitFiniSerializer, 
    StockSerializer, MouvementStockSerializer
)
from users_app.permissions import (
    IsAdminOrReadOnly, IsMagasinierOrAdmin, CanViewStock, CanManageInventory, IsAdmin, 
    CanViewWarehouseStock, CanManageWarehouseStock, HasWarehouseObjectPermission
)
from users_app.permissions import get_user_accessible_warehouses, get_user_warehouse_permissions

class MatierePremiereViewSet(viewsets.ModelViewSet):
    queryset = MatierePremiere.objects.filter(est_archive=False)
    serializer_class = MatierePremiereSerializer
    permission_classes = [CanViewStock]  # All roles can view raw materials

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]  # Only admin can modify raw materials
        return [CanViewStock()]  # All roles can view

    def perform_destroy(self, instance):
        instance.est_archive = True
        instance.save()

class ProduitSemiFiniViewSet(viewsets.ModelViewSet):
    queryset = ProduitSemiFini.objects.filter(est_archive=False)
    serializer_class = ProduitSemiFiniSerializer
    permission_classes = [IsAdminOrReadOnly]  # Only admin can manage

    def perform_destroy(self, instance):
        instance.est_archive = True
        instance.save()

class ProduitFiniViewSet(viewsets.ModelViewSet):
    queryset = ProduitFini.objects.filter(est_archive=False)
    serializer_class = ProduitFiniSerializer
    permission_classes = [IsAdminOrReadOnly]  # Only admin can manage

    def perform_destroy(self, instance):
        instance.est_archive = True
        instance.save()

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all().select_related('entrepot')  # Default queryset
    serializer_class = StockSerializer
    permission_classes = [CanViewWarehouseStock, HasWarehouseObjectPermission]  # Use warehouse-specific permissions

    def get_queryset(self):
        """
        Filter stock based on user's warehouse permissions
        """
        if not self.request.user.is_authenticated:
            return Stock.objects.none()
        
        # Get accessible warehouses for the user
        accessible_warehouses = get_user_accessible_warehouses(self.request.user)
        
        # Filter stock by accessible warehouses
        return Stock.objects.filter(entrepot__in=accessible_warehouses).select_related('entrepot')

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [CanManageWarehouseStock(), HasWarehouseObjectPermission()]  # Only magasiniers with warehouse access can manage
        return [CanViewWarehouseStock(), HasWarehouseObjectPermission()]  # All roles with warehouse access can view

    def perform_create(self, serializer):
        serializer.save()

class MouvementStockViewSet(viewsets.ModelViewSet):
    queryset = MouvementStock.objects.all().select_related('entrepot', 'utilisateur')  # Default queryset
    serializer_class = MouvementStockSerializer
    permission_classes = [CanViewWarehouseStock, HasWarehouseObjectPermission]  # Use warehouse-specific permissions

    def get_queryset(self):
        """
        Filter stock movements based on user's warehouse permissions
        """
        if not self.request.user.is_authenticated:
            return MouvementStock.objects.none()
        
        # Get accessible warehouses for the user
        accessible_warehouses = get_user_accessible_warehouses(self.request.user)
        
        # Filter movements by accessible warehouses
        return MouvementStock.objects.filter(
            entrepot__in=accessible_warehouses
        ).select_related('entrepot', 'utilisateur')

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [CanManageWarehouseStock(), HasWarehouseObjectPermission()]  # Only magasiniers with warehouse access can manage
        return [CanViewWarehouseStock(), HasWarehouseObjectPermission()]  # All roles with warehouse access can view

    def perform_create(self, serializer):
        # Automatically set the user who created the movement
        serializer.save(utilisateur=self.request.user.utilisateur)

    @action(detail=False, methods=['get'])
    def par_article(self, request):
        """Get movements for a specific article"""
        content_type_id = request.query_params.get('content_type')
        id_article = request.query_params.get('id_article')
        entrepot_id = request.query_params.get('entrepot')
        
        if not content_type_id or not id_article:
            return Response(
                {"error": "content_type et id_article sont requis"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.queryset.filter(
            content_type_id=content_type_id,
            id_article=id_article
        )
        
        if entrepot_id:
            queryset = queryset.filter(entrepot_id=entrepot_id)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
