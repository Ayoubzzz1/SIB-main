# sib/utils.py
"""
Utility functions for SIB admin interface with Unfold UI
"""

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


def environment_callback(request):
    """
    Callback to show environment information in the admin
    """
    if hasattr(request, 'user') and request.user and request.user.is_authenticated:
        if request.user.is_superuser:
            return ["Développement", "success"]
        else:
            return ["Production", "danger"]
    return ["Système", "info"]


def dashboard_callback(request, context):
    """
    Callback to customize the admin dashboard
    Unfold expects a dictionary to be returned, not a list
    """
    # Import here to avoid circular imports
    try:
        from django.contrib.auth.models import User
        from inventory_app.models import Stock
        from sales_app.models import Client, Commande
        from warehouse.models import Entrepot
        
        # Get statistics for dashboard
        total_users = User.objects.count()
        total_clients = Client.objects.count() 
        total_stock_items = Stock.objects.count()
        total_orders = Commande.objects.count()
        total_warehouses = Entrepot.objects.count()
        
        # Low stock alerts
        low_stock_items = Stock.objects.filter(quantite_actuelle__lt=10).count()
        
        # Return dictionary with dashboard data
        dashboard_data = {
            'total_users': total_users,
            'total_clients': total_clients,
            'total_stock_items': total_stock_items,
            'total_orders': total_orders,
            'total_warehouses': total_warehouses,
            'low_stock_items': low_stock_items,
            'stock_status': 'Attention: Stock faible' if low_stock_items > 0 else 'Stock normal',
        }
        
        # Update context with our data
        context.update(dashboard_data)
        return context
        
    except Exception as e:
        # Return original context if models are not ready (during migrations, etc.)
        return context


def get_admin_url(model_name, app_name, action="changelist"):
    """
    Helper function to generate admin URLs
    """
    return reverse_lazy(f"admin:{app_name}_{model_name}_{action}")


# Quick links for different user roles
def get_quick_links_for_user(user):
    """
    Return relevant quick links based on user permissions
    """
    links = []
    
    # Basic links for all users
    links.extend([
        {
            "title": _("Mon Profil"),
            "url": reverse_lazy("admin:auth_user_change", args=[user.pk]),
            "icon": "person"
        }
    ])
    
    # Inventory management links
    if user.has_perm('inventory_app.view_stock'):
        links.extend([
            {
                "title": _("Voir Stock"),
                "url": reverse_lazy("admin:inventory_app_stock_changelist"),
                "icon": "inventory"
            },
            {
                "title": _("Mouvements Stock"),
                "url": reverse_lazy("admin:inventory_app_mouvementstock_changelist"), 
                "icon": "swap_horiz"
            }
        ])
    
    # Sales links
    if user.has_perm('sales_app.view_client'):
        links.extend([
            {
                "title": _("Clients"),
                "url": reverse_lazy("admin:sales_app_client_changelist"),
                "icon": "people"
            },
            {
                "title": _("Nouvelle Commande"),
                "url": reverse_lazy("admin:sales_app_commande_add"),
                "icon": "add_shopping_cart"
            }
        ])
    
    # Production links
    if user.has_perm('production_app.view_production'):
        links.append({
            "title": _("Productions"),
            "url": reverse_lazy("admin:production_app_production_changelist"),
            "icon": "precision_manufacturing"
        })
    
    return links