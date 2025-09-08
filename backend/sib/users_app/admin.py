from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.contrib.auth.models import User
from .models import Utilisateur, UtilisateurEntrepot
from .forms import CustomUserCreationForm

# Enhanced inline for warehouse access with better organization
class UtilisateurEntrepotInline(admin.TabularInline):
    model = UtilisateurEntrepot
    extra = 1
    fields = ('entrepot', 'peut_lire', 'peut_modifier', 'peut_supprimer')
    verbose_name = "Accès à l'entrepôt"
    verbose_name_plural = "Accès aux entrepôts"
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        form.base_fields['peut_lire'].help_text = "L'utilisateur peut voir les données de cet entrepôt"
        form.base_fields['peut_modifier'].help_text = "L'utilisateur peut modifier les données de cet entrepôt"
        form.base_fields['peut_supprimer'].help_text = "L'utilisateur peut supprimer les données de cet entrepôt"
        return formset

# Enhanced inline for user profile with all required fields
class UtilisateurInline(admin.StackedInline):
    model = Utilisateur
    extra = 0
    fields = (
        ('nom', 'statut_equipe'),
        ('acces_tous_entrepots',),
        'cree_le'
    )
    readonly_fields = ('cree_le',)
    verbose_name = "Profil Utilisateur"
    verbose_name_plural = "Profil Utilisateur"
    inlines = [UtilisateurEntrepotInline]
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        form.base_fields['nom'].help_text = "Nom complet de l'utilisateur"
        form.base_fields['statut_equipe'].help_text = "Statut actuel de l'utilisateur dans l'équipe"
        form.base_fields['acces_tous_entrepots'].help_text = "Si activé, l'utilisateur a accès à tous les entrepôts"
        return formset

# Enhanced admin for User model with comprehensive form and list display
class EnhancedUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    inlines = [UtilisateurInline]
    
    # Comprehensive list display showing all important data
    list_display = (
        'username', 
        'get_full_name_display', 
        'email', 
        'get_groups_display',
        'get_team_status_display',
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
        'utilisateur__statut_equipe',
        'utilisateur__acces_tous_entrepots',
        'date_joined'
    )
    
    search_fields = ('username', 'utilisateur__nom', 'email', 'first_name', 'last_name')
    
    # Make important fields editable in the list
    list_editable = ('is_active', 'is_staff', 'is_superuser')
    
    # Enhanced form fields organization
    fieldsets = (
        ('Informations de base', {
            'fields': ('username', 'password')
        }),
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'description': 'Gérez les permissions et le statut de l\'utilisateur'
        }),
        ('Dates importantes', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Informations de base', {
            'fields': ('username', 'password1', 'password2'),
            'description': 'Informations de connexion'
        }),
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'email'),
            'description': 'Informations personnelles de l\'utilisateur'
        }),
        ('Permissions initiales', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups'),
            'description': 'Définissez le statut et les groupes de l\'utilisateur'
        }),
    )
    
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

    def get_team_status_display(self, obj):
        """Display team status from Utilisateur model"""
        try:
            if hasattr(obj, 'utilisateur') and obj.utilisateur:
                status = obj.utilisateur.get_statut_equipe_display()
                if obj.utilisateur.statut_equipe == 'actif':
                    return f"✅ {status}"
                elif obj.utilisateur.statut_equipe == 'inactif':
                    return f"❌ {status}"
                elif obj.utilisateur.statut_equipe == 'vacances':
                    return f"🏖️ {status}"
                elif obj.utilisateur.statut_equipe == 'maladie':
                    return f"🏥 {status}"
                elif obj.utilisateur.statut_equipe == 'formation':
                    return f"📚 {status}"
                else:
                    return f"❓ {status}"
            else:
                return "⚠️ Pas de profil"
        except:
            return "❓ Erreur"
    get_team_status_display.short_description = 'Statut Équipe'

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
admin.site.register(User, EnhancedUserAdmin)

# Simple admin for Utilisateur (hidden from main sidebar)
@admin.register(Utilisateur)
class SimpleUtilisateurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'user', 'statut_equipe', 'acces_tous_entrepots', 'cree_le')
    list_filter = ('statut_equipe', 'acces_tous_entrepots', 'cree_le')
    search_fields = ('nom', 'user__username')
    readonly_fields = ('cree_le',)
    inlines = [UtilisateurEntrepotInline]
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('user', 'nom')
        }),
        ('Statut et permissions', {
            'fields': ('statut_equipe', 'acces_tous_entrepots'),
            'description': 'Gérez le statut de l\'équipe et l\'accès aux entrepôts'
        }),
        ('Informations système', {
            'fields': ('cree_le',),
            'classes': ('collapse',)
        }),
    )
    
    def get_model_perms(self, request):
        return {}  # Hide from main sidebar

# Warehouse access admin - VISIBLE in sidebar
@admin.register(UtilisateurEntrepot)
class UtilisateurEntrepotAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'entrepot', 'peut_lire', 'peut_modifier', 'peut_supprimer', 'date_creation')
    list_filter = ('peut_lire', 'peut_modifier', 'peut_supprimer', 'entrepot', 'date_creation')
    search_fields = ('utilisateur__nom', 'utilisateur__user__username', 'entrepot__nom')
    readonly_fields = ('date_creation',)
    
    # Fields for editing with better organization
    fieldsets = (
        ('Accès utilisateur-entrepôt', {
            'fields': ('utilisateur', 'entrepot')
        }),
        ('Permissions', {
            'fields': ('peut_lire', 'peut_modifier', 'peut_supprimer'),
            'description': 'Définissez les permissions de l\'utilisateur sur cet entrepôt'
        }),
        ('Informations système', {
            'fields': ('date_creation',),
            'classes': ('collapse',)
        }),
    )
    
    # Make it easy to add new warehouse access
    list_editable = ('peut_lire', 'peut_modifier', 'peut_supprimer')
    
    # Show in sidebar
    def get_model_perms(self, request):
        # Return default permissions to show in sidebar
        return super().get_model_perms(request)
