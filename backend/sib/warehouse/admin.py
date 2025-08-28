from django.contrib import admin
from .models import Entrepot
from users_app.permissions import get_user_accessible_warehouses

@admin.register(Entrepot)
class EntrepotAdmin(admin.ModelAdmin):
    list_display = ('nom', 'adresse', 'description', 'cree_le')
    list_filter = ('cree_le',)
    search_fields = ('nom', 'adresse', 'description')
    readonly_fields = ('cree_le',)
    
    def get_queryset(self, request):
        """Filter warehouses based on user's permissions"""
        qs = super().get_queryset(request)
        
        # If user has access to all warehouses, show everything
        if hasattr(request.user, 'utilisateur') and request.user.utilisateur:
            if request.user.utilisateur.acces_tous_entrepots:
                return qs
            else:
                # Only show warehouses the user has access to
                accessible_warehouses = get_user_accessible_warehouses(request.user)
                return qs.filter(id__in=accessible_warehouses.values_list('id', flat=True))
        
        return qs
