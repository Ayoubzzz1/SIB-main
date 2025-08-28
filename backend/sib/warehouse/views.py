from django.shortcuts import render
from rest_framework import viewsets
from .models import Entrepot
from .serializers import EntrepotSerializer
from users_app.permissions import CanManageInventory, CanAccessWarehouse, get_user_accessible_warehouses, HasWarehouseObjectPermission
from logs_app.mixins import LoggingMixin

# Create your views here.

class EntrepotViewSet(LoggingMixin, viewsets.ModelViewSet):
    queryset = Entrepot.objects.all()  # Default queryset
    serializer_class = EntrepotSerializer
    permission_classes = [CanAccessWarehouse, HasWarehouseObjectPermission]  # Use warehouse-specific permissions

    def get_queryset(self):
        """
        Filter warehouses based on user's permissions
        """
        if not self.request.user.is_authenticated:
            return Entrepot.objects.none()
        
        # Return only warehouses the user has access to
        return get_user_accessible_warehouses(self.request.user)
