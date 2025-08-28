from rest_framework import permissions
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404
from warehouse.models import Entrepot
from .models import Utilisateur

# Base permission classes that work with Django groups
class HasGroupPermission(permissions.BasePermission):
    """
    Base permission class that checks if user belongs to specific groups
    """
    required_groups = []
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Superuser has all permissions
        if request.user.is_superuser:
            return True
        
        # Check if user belongs to any of the required groups
        user_groups = request.user.groups.all()
        return any(group.name in self.required_groups for group in user_groups)

class IsAdminOrReadOnly(HasGroupPermission):
    """
    Allow admins to write, authenticated users to read
    """
    required_groups = ['Administrateurs']
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return super().has_permission(request, view)

class IsAdmin(HasGroupPermission):
    """
    Only allow administrators
    """
    required_groups = ['Administrateurs']

class IsMagasinierOrAdmin(HasGroupPermission):
    """
    Allow warehouse workers and administrators
    """
    required_groups = ['Magasiniers', 'Administrateurs']

class IsCommercialOrAdmin(HasGroupPermission):
    """
    Allow sales people and administrators
    """
    required_groups = ['Commerciaux', 'Administrateurs']

class IsProductionOrAdmin(HasGroupPermission):
    """
    Allow production workers and administrators
    """
    required_groups = ['Ouvriers de production', 'Administrateurs']

# Warehouse-specific permission classes
class HasWarehouseAccess(permissions.BasePermission):
    """
    Base permission class for warehouse access
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Superuser has access to all warehouses
        if request.user.is_superuser:
            return True
        
        # Check if user has any warehouse access
        try:
            utilisateur = request.user.utilisateur
            if utilisateur.acces_tous_entrepots:
                return True
            return utilisateur.entrepots_autorises.exists()
        except Utilisateur.DoesNotExist:
            return False

class CanViewWarehouseStock(HasWarehouseAccess):
    """
    Permission to view warehouse stock
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        # Check if user belongs to groups that can view stock
        user_groups = request.user.groups.all()
        allowed_groups = ['Commerciaux', 'Magasiniers', 'Ouvriers de production', 'Administrateurs']
        return any(group.name in allowed_groups for group in user_groups)

class CanManageWarehouseStock(HasWarehouseAccess):
    """
    Permission to manage warehouse stock
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        # Check if user belongs to groups that can manage stock
        user_groups = request.user.groups.all()
        allowed_groups = ['Magasiniers', 'Administrateurs']
        return any(group.name in allowed_groups for group in user_groups)

class CanAccessWarehouse(HasWarehouseAccess):
    """
    Permission to access warehouse data
    """
    pass

# Specific business logic permissions
class CanViewStock(HasGroupPermission):
    """
    Permission to view stock (Commerciaux, Magasiniers, Production, Admin)
    """
    required_groups = ['Commerciaux', 'Magasiniers', 'Ouvriers de production', 'Administrateurs']

class CanManageOrders(HasGroupPermission):
    """
    Permission to manage orders (Commerciaux, Admin)
    """
    required_groups = ['Commerciaux', 'Administrateurs']

class CanViewOrders(HasGroupPermission):
    """
    Permission to view orders (Magasiniers, Production, Admin)
    """
    required_groups = ['Magasiniers', 'Ouvriers de production', 'Administrateurs']

class CanManageClients(HasGroupPermission):
    """
    Permission to manage clients (Commerciaux, Admin)
    """
    required_groups = ['Commerciaux', 'Administrateurs']

class CanManageSuppliers(HasGroupPermission):
    """
    Permission to manage suppliers (Commerciaux, Admin)
    """
    required_groups = ['Commerciaux', 'Administrateurs']

class CanManageInventory(HasGroupPermission):
    """
    Permission to manage inventory (Magasiniers, Admin)
    """
    required_groups = ['Magasiniers', 'Administrateurs']

class CanManageProduction(HasGroupPermission):
    """
    Permission to manage production (Production, Admin)
    """
    required_groups = ['Ouvriers de production', 'Administrateurs']

class CanManageUsers(HasGroupPermission):
    """
    Permission to manage users (Admin only)
    """
    required_groups = ['Administrateurs']

class CanViewLogs(HasGroupPermission):
    """
    Permission to view logs (Admin only)
    """
    required_groups = ['Administrateurs']

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to allow object owner or administrator
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Superuser has all permissions
        if request.user.is_superuser:
            return True
        
        # Check if user belongs to Administrateurs group
        user_groups = request.user.groups.all()
        if any(group.name == 'Administrateurs' for group in user_groups):
            return True
        
        # Check if user is the owner of the object
        if hasattr(obj, 'id_expediteur'):
            return obj.id_expediteur == request.user.utilisateur
        elif hasattr(obj, 'cree_par'):
            return obj.cree_par == request.user.utilisateur
        elif hasattr(obj, 'utilisateur'):
            return obj.utilisateur == request.user.utilisateur
        
        return False

# Object-level permissions for warehouse access
class HasWarehouseObjectPermission(permissions.BasePermission):
    """
    Check if user has access to a specific warehouse object
    """
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Superuser has access to all objects
        if request.user.is_superuser:
            return True
        
        # Get the warehouse from the object
        entrepot = None
        if hasattr(obj, 'entrepot'):
            entrepot = obj.entrepot
        elif hasattr(obj, 'entrepot_source'):
            entrepot = obj.entrepot_source
        elif hasattr(obj, 'entrepot_destination'):
            entrepot = obj.entrepot_destination
        
        if not entrepot:
            return False
        
        # Check warehouse access
        try:
            utilisateur = request.user.utilisateur
            if utilisateur.acces_tous_entrepots:
                return True
            return utilisateur.entrepots_autorises.filter(entrepot=entrepot).exists()
        except Utilisateur.DoesNotExist:
            return False

# Utility functions for warehouse access
def get_user_warehouse_permissions(user, entrepot):
    """
    Get warehouse-specific permissions for a user
    Returns a dict with permissions: {'read': True, 'write': False, 'delete': False}
    """
    try:
        utilisateur = user.utilisateur
    except Utilisateur.DoesNotExist:
        return {'read': False, 'write': False, 'delete': False}
    
    # If user has access to all warehouses
    if utilisateur.acces_tous_entrepots:
        return {'read': True, 'write': True, 'delete': True}
    
    # Check specific warehouse permissions
    try:
        access = utilisateur.entrepots_autorises.get(entrepot=entrepot)
        return {
            'read': access.peut_lire,
            'write': access.peut_modifier,
            'delete': access.peut_supprimer
        }
    except:
        return {'read': False, 'write': False, 'delete': False}

def get_user_accessible_warehouses(user):
    """
    Get all warehouses a user has access to
    """
    try:
        utilisateur = user.utilisateur
    except Utilisateur.DoesNotExist:
        return Entrepot.objects.none()
    
    if utilisateur.acces_tous_entrepots:
        return Entrepot.objects.all()
    
    return Entrepot.objects.filter(utilisateurs_autorises__utilisateur=utilisateur).distinct()

def require_warehouse_access(permission_type='read'):
    """
    Decorator to require warehouse access
    Usage: @require_warehouse_access('read') or @require_warehouse_access('write')
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            # Get warehouse from URL parameters or request
            entrepot_id = kwargs.get('entrepot_id') or request.GET.get('entrepot_id') or request.POST.get('entrepot_id')
            
            if not entrepot_id:
                raise Http404("Entrepôt non spécifié")
            
            entrepot = get_object_or_404(Entrepot, id=entrepot_id)
            permissions = get_user_warehouse_permissions(request.user, entrepot)
            
            if not permissions.get(permission_type, False):
                raise PermissionDenied(f"Vous n'avez pas les permissions {permission_type} pour cet entrepôt")
            
            # Add warehouse to request for use in view
            request.current_warehouse = entrepot
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def filter_queryset_by_warehouse_access(queryset, user, warehouse_field='entrepot'):
    """
    Filter a queryset to only show items from warehouses the user has access to
    """
    accessible_warehouses = get_user_accessible_warehouses(user)
    return queryset.filter(**{f'{warehouse_field}__in': accessible_warehouses})

class WarehouseAccessMixin:
    """
    Mixin for views to automatically filter by warehouse access
    """
    warehouse_field = 'entrepot'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return filter_queryset_by_warehouse_access(queryset, self.request.user, self.warehouse_field)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accessible_warehouses'] = get_user_accessible_warehouses(self.request.user)
        return context

def create_warehouse_permissions():
    """
    Create custom permissions for warehouse access
    """
    content_type = ContentType.objects.get_for_model(Entrepot)
    
    permissions = [
        ('can_access_warehouse', 'Can access warehouse'),
        ('can_read_warehouse', 'Can read warehouse data'),
        ('can_write_warehouse', 'Can write warehouse data'),
        ('can_delete_warehouse', 'Can delete warehouse data'),
    ]
    
    created_permissions = []
    for codename, name in permissions:
        permission, created = Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type,
        )
        if created:
            created_permissions.append(permission)
    
    return created_permissions

def assign_warehouse_permissions_to_groups():
    """
    Assign warehouse permissions to groups based on their roles
    """
    from django.contrib.auth.models import Group
    
    # Get groups
    commerciaux = Group.objects.get(name='Commerciaux')
    magasiniers = Group.objects.get(name='Magasiniers')
    ouvriers = Group.objects.get(name='Ouvriers de production')
    administrateurs = Group.objects.get(name='Administrateurs')
    
    # Get warehouse permissions
    content_type = ContentType.objects.get_for_model(Entrepot)
    warehouse_permissions = Permission.objects.filter(content_type=content_type)
    
    # Assign permissions to groups
    # Commerciaux: read access to all warehouses
    commerciaux.permissions.add(
        *warehouse_permissions.filter(codename='can_read_warehouse')
    )
    
    # Magasiniers: read and write access to all warehouses
    magasiniers.permissions.add(
        *warehouse_permissions.filter(codename__in=['can_read_warehouse', 'can_write_warehouse'])
    )
    
    # Ouvriers: read access to all warehouses
    ouvriers.permissions.add(
        *warehouse_permissions.filter(codename='can_read_warehouse')
    )
    
    # Administrateurs: all permissions
    administrateurs.permissions.add(*warehouse_permissions)
