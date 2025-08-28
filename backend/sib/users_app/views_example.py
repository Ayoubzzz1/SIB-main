from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users_app.permissions import (
    require_warehouse_access, 
    WarehouseAccessMixin, 
    filter_queryset_by_warehouse_access,
    get_user_warehouse_permissions,
    get_user_accessible_warehouses
)
from warehouse.models import Entrepot
from inventory_app.models import MatierePremiere, ProduitFini
from sales_app.models import Commande

# Example 1: Function-based view with decorator
@login_required
@require_warehouse_access('read')
def warehouse_detail_view(request, entrepot_id):
    """
    View warehouse details - automatically checks access
    """
    # request.current_warehouse is automatically set by the decorator
    entrepot = request.current_warehouse
    
    # Get warehouse permissions for this user
    permissions = get_user_warehouse_permissions(request.user, entrepot)
    
    context = {
        'entrepot': entrepot,
        'permissions': permissions,
        'can_edit': permissions.get('write', False),
        'can_delete': permissions.get('delete', False),
    }
    
    return render(request, 'warehouse/detail.html', context)

# Example 2: Class-based view with mixin
class WarehouseListView(LoginRequiredMixin, WarehouseAccessMixin, ListView):
    """
    List warehouses - automatically filters by user access
    """
    model = Entrepot
    template_name = 'warehouse/list.html'
    context_object_name = 'warehouses'
    
    def get_queryset(self):
        # Automatically filtered by warehouse access
        return super().get_queryset()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # accessible_warehouses is automatically added by the mixin
        context['accessible_warehouses'] = self.request.accessible_warehouses
        return context

# Example 3: Inventory view with warehouse filtering
class InventoryListView(LoginRequiredMixin, ListView):
    """
    List inventory items filtered by warehouse access
    """
    model = MatierePremiere
    template_name = 'inventory/list.html'
    context_object_name = 'materials'
    
    def get_queryset(self):
        # Filter by warehouse access
        return filter_queryset_by_warehouse_access(
            super().get_queryset(), 
            self.request.user, 
            'entrepot'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accessible_warehouses'] = get_user_accessible_warehouses(self.request.user)
        return context

# Example 4: API ViewSet with warehouse filtering
class WarehouseViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for warehouses with automatic access filtering
    """
    model = Entrepot
    
    def get_queryset(self):
        # Filter by user's accessible warehouses
        return get_user_accessible_warehouses(self.request.user)
    
    @action(detail=True, methods=['get'])
    def inventory(self, request, pk=None):
        """
        Get inventory for a specific warehouse
        """
        entrepot = self.get_object()
        
        # Check if user has access to this warehouse
        if not request.has_warehouse_access(entrepot.id):
            raise PermissionDenied("Vous n'avez pas accès à cet entrepôt")
        
        # Get inventory data
        materials = MatierePremiere.objects.filter(entrepot=entrepot)
        products = ProduitFini.objects.filter(entrepot=entrepot)
        
        return Response({
            'entrepot': entrepot.nom,
            'materials': materials.count(),
            'products': products.count(),
        })

# Example 5: Order view with warehouse access
@login_required
@require_warehouse_access('write')
def create_order_view(request, entrepot_id):
    """
    Create an order for a specific warehouse
    """
    entrepot = request.current_warehouse
    
    if request.method == 'POST':
        # Process order creation
        # The decorator ensures user has write access to this warehouse
        pass
    
    context = {
        'entrepot': entrepot,
        'materials': MatierePremiere.objects.filter(entrepot=entrepot),
    }
    
    return render(request, 'orders/create.html', context)

# Example 6: Custom permission check
@login_required
def warehouse_operations_view(request, entrepot_id):
    """
    View that manually checks warehouse permissions
    """
    entrepot = get_object_or_404(Entrepot, id=entrepot_id)
    permissions = get_user_warehouse_permissions(request.user, entrepot)
    
    if not permissions.get('read', False):
        raise PermissionDenied("Vous n'avez pas accès à cet entrepôt")
    
    # Perform operations based on permissions
    operations = []
    
    if permissions.get('read', False):
        operations.append('Voir le stock')
    
    if permissions.get('write', False):
        operations.append('Modifier le stock')
        operations.append('Créer des commandes')
    
    if permissions.get('delete', False):
        operations.append('Supprimer des éléments')
    
    context = {
        'entrepot': entrepot,
        'permissions': permissions,
        'operations': operations,
    }
    
    return render(request, 'warehouse/operations.html', context)

# Example 7: Template context processor (add to settings.py)
def warehouse_context_processor(request):
    """
    Add warehouse access information to all templates
    """
    if hasattr(request, 'user') and request.user.is_authenticated:
        return {
            'accessible_warehouses': get_user_accessible_warehouses(request.user),
            'has_warehouse_access': request.has_warehouse_access if hasattr(request, 'has_warehouse_access') else lambda x: False,
        }
    return {}

