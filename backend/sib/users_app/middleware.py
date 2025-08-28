from django.utils.deprecation import MiddlewareMixin
from users_app.permissions import get_user_accessible_warehouses

class WarehouseAccessMiddleware(MiddlewareMixin):
    """
    Middleware to automatically add warehouse access information to requests
    """
    
    def process_request(self, request):
        """
        Add warehouse access information to the request
        """
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Add accessible warehouses to request
            request.accessible_warehouses = get_user_accessible_warehouses(request.user)
            
            # Add a helper method to check warehouse access
            def has_warehouse_access(warehouse_id):
                return request.accessible_warehouses.filter(id=warehouse_id).exists()
            
            request.has_warehouse_access = has_warehouse_access

class WarehouseFilterMiddleware(MiddlewareMixin):
    """
    Middleware to automatically filter querysets by warehouse access
    """
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Process the view and add warehouse filtering if needed
        """
        # Only apply to authenticated users
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
        
        # Check if the view has warehouse filtering enabled
        if hasattr(view_func, 'warehouse_filter_enabled') and view_func.warehouse_filter_enabled:
            # The view will handle its own filtering
            return None
        
        # For API views, we'll let the view handle filtering
        if 'api' in request.path:
            return None
        
        return None

