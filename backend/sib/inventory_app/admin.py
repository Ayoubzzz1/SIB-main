from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.urls import path
from .models import MatierePremiere, ProduitSemiFini, ProduitFini, Stock, MouvementStock
from django.utils import timezone
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
from users_app.permissions import get_user_accessible_warehouses

class WarehouseAccessFilter(admin.SimpleListFilter):
    title = 'Entrepôt'
    parameter_name = 'entrepot'

    def lookups(self, request, model_admin):
        # Get warehouses the current user has access to
        if hasattr(request.user, 'utilisateur') and request.user.utilisateur:
            if request.user.utilisateur.acces_tous_entrepots:
                # User has access to all warehouses
                from warehouse.models import Entrepot
                return [(w.id, w.nom) for w in Entrepot.objects.all()]
            else:
                # User only has access to specific warehouses
                accessible_warehouses = request.user.utilisateur.entrepots_autorises.all()
                return [(w.entrepot.id, w.entrepot.nom) for w in accessible_warehouses]
        return []

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(entrepot_id=self.value())
        return queryset

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('get_article_name', 'type_article', 'quantite', 'entrepot', 'derniere_maj')
    list_filter = (WarehouseAccessFilter, 'type_article', 'entrepot', 'derniere_maj')
    search_fields = ('entrepot__nom',)
    readonly_fields = ('derniere_maj',)
    
    def get_queryset(self, request):
        """Filter stock based on user's warehouse permissions"""
        qs = super().get_queryset(request)
        
        # If user has access to all warehouses, show everything
        if hasattr(request.user, 'utilisateur') and request.user.utilisateur:
            if request.user.utilisateur.acces_tous_entrepots:
                return qs
            else:
                # Only show stock from accessible warehouses
                accessible_warehouses = get_user_accessible_warehouses(request.user)
                return qs.filter(entrepot__in=accessible_warehouses)
        
        return qs
    
    def get_article_name(self, obj):
        """Get the name of the article"""
        if obj.article:
            return str(obj.article)
        return f"{obj.get_type_article_display()} #{obj.id_article}"
    get_article_name.short_description = 'Article'

@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ('get_article_name', 'type_mouvement', 'quantite', 'entrepot', 'utilisateur', 'date_mouvement')
    list_filter = (WarehouseAccessFilter, 'type_mouvement', 'entrepot', 'date_mouvement')
    search_fields = ('entrepot__nom', 'utilisateur__nom')
    readonly_fields = ('date_mouvement',)
    
    def get_queryset(self, request):
        """Filter stock movements based on user's warehouse permissions"""
        qs = super().get_queryset(request)
        
        # If user has access to all warehouses, show everything
        if hasattr(request.user, 'utilisateur') and request.user.utilisateur:
            if request.user.utilisateur.acces_tous_entrepots:
                return qs
            else:
                # Only show movements from accessible warehouses
                accessible_warehouses = get_user_accessible_warehouses(request.user)
                return qs.filter(entrepot__in=accessible_warehouses)
        
        return qs
    
    def get_article_name(self, obj):
        """Get the name of the article"""
        if obj.article:
            return str(obj.article)
        return f"{obj.content_type.model} #{obj.id_article}"
    get_article_name.short_description = 'Article'

@admin.register(MatierePremiere)
class MatierePremiereAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code_reference', 'unite', 'niveau_min_stock', 'est_archive', 'cree_le')
    list_filter = ('est_archive', 'unite', 'cree_le')
    search_fields = ('nom', 'code_reference')
    readonly_fields = ('cree_le',)

@admin.register(ProduitSemiFini)
class ProduitSemiFiniAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code_reference', 'unite', 'niveau_min_stock', 'est_archive', 'cree_le')
    list_filter = ('est_archive', 'unite', 'cree_le')
    search_fields = ('nom', 'code_reference')
    readonly_fields = ('cree_le',)

@admin.register(ProduitFini)
class ProduitFiniAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code_reference', 'unite', 'niveau_min_stock', 'est_archive', 'cree_le')
    list_filter = ('est_archive', 'unite', 'cree_le')
    search_fields = ('nom', 'code_reference')
    readonly_fields = ('cree_le',)
