from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.contrib.auth.models import User
from .models import Utilisateur, UtilisateurEntrepot

# Simple inline for warehouse access
class UtilisateurEntrepotInline(admin.TabularInline):
    model = UtilisateurEntrepot
    extra = 1
    fields = ('entrepot', 'peut_lire', 'peut_modifier', 'peut_supprimer')
    verbose_name = "Accès à l'entrepôt"
    verbose_name_plural = "Accès aux entrepôts"

# Simple inline for user profile
class UtilisateurInline(admin.StackedInline):
    model = Utilisateur
    extra = 0
    fields = ('nom', 'acces_tous_entrepots', 'cree_le')
    readonly_fields = ('cree_le',)
    verbose_name = "Profil Utilisateur"
    verbose_name_plural = "Profil Utilisateur"
    inlines = [UtilisateurEntrepotInline]

# Enhanced admin for User model with comprehensive list display
class SimpleUserAdmin(UserAdmin):
    inlines = [UtilisateurInline]
    
    # Comprehensive list display showing all important data
    list_display = (
        'username', 
        'get_full_name_display', 
        'email', 
        'get_groups_display',
        'get_warehouse_access_display',
        'is_active', 
        'is_staff', 
        'is_superuser',
        'date_joined',
        'last_login'
    )
    
    list_filter = (
        'is_active', 
        'is_staff', 
        'is_superuser', 
        'groups',
        'utilisateur__acces_tous_entrepots',
        'date_joined'
    )
    
    search_fields = ('username', 'utilisateur__nom', 'email', 'first_name', 'last_name')
    
    # Make important fields editable in the list
    list_editable = ('is_active', 'is_staff', 'is_superuser')
    
    # Enhanced list display methods
    def get_full_name_display(self, obj):
        """Display full name from Utilisateur model or Django User"""
        try:
            if hasattr(obj, 'utilisateur') and obj.utilisateur and obj.utilisateur.nom:
                return obj.utilisateur.nom
            else:
                return f"{obj.first_name} {obj.last_name}".strip() or obj.username
        except:
            return f"{obj.first_name} {obj.last_name}".strip() or obj.username
    get_full_name_display.short_description = 'Nom Complet'

    def get_groups_display(self, obj):
        """Display groups as comma-separated list"""
        groups = obj.groups.all()
        if groups:
            return ", ".join([group.name for group in groups])
        return "Aucun groupe"
    get_groups_display.short_description = 'Groupes'

    def get_warehouse_access_display(self, obj):
        """Display warehouse access status"""
        try:
            if hasattr(obj, 'utilisateur') and obj.utilisateur:
                if obj.utilisateur.acces_tous_entrepots:
                    return "🔓 Tous les entrepôts"
                elif obj.utilisateur.entrepots_autorises.exists():
                    count = obj.utilisateur.entrepots_autorises.count()
                    return f"🔒 {count} entrepôt(s)"
                else:
                    return "❌ Aucun accès"
            else:
                return "⚠️ Pas de profil"
        except:
            return "❓ Erreur"
    get_warehouse_access_display.short_description = 'Accès Entrepôts'

# Register the enhanced admin
admin.site.unregister(User)
admin.site.register(User, SimpleUserAdmin)

# Simple admin for Utilisateur (hidden from main sidebar)
@admin.register(Utilisateur)
class SimpleUtilisateurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'user', 'acces_tous_entrepots', 'cree_le')
    list_filter = ('acces_tous_entrepots', 'cree_le')
    search_fields = ('nom', 'user__username')
    readonly_fields = ('cree_le',)
    inlines = [UtilisateurEntrepotInline]
    
    def get_model_perms(self, request):
        return {}  # Hide from main sidebar

# Warehouse access admin - VISIBLE in sidebar
@admin.register(UtilisateurEntrepot)
class UtilisateurEntrepotAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'entrepot', 'peut_lire', 'peut_modifier', 'peut_supprimer', 'date_creation')
    list_filter = ('peut_lire', 'peut_modifier', 'peut_supprimer', 'entrepot', 'date_creation')
    search_fields = ('utilisateur__nom', 'utilisateur__user__username', 'entrepot__nom')
    readonly_fields = ('date_creation',)
    
    # Fields for editing
    fields = ('utilisateur', 'entrepot', 'peut_lire', 'peut_modifier', 'peut_supprimer', 'date_creation')
    
    # Make it easy to add new warehouse access
    list_editable = ('peut_lire', 'peut_modifier', 'peut_supprimer')
    
    # Show in sidebar
    def get_model_perms(self, request):
        # Return default permissions to show in sidebar
        return super().get_model_perms(request)
