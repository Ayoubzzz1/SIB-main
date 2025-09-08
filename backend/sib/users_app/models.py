from django.db import models
from django.contrib.auth.models import User # Importez le modèle User de Django

class Utilisateur(models.Model):
    # Lien OneToOne avec le modèle User de Django pour l'authentification
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='utilisateur', verbose_name="Compte Utilisateur Django")

    nom = models.CharField(max_length=255, verbose_name="Nom Complet")
    # L'email sera géré par le modèle User de Django
    # mot_de_passe_hash ne sera plus nécessaire ici si vous utilisez le système d'auth de Django
    cree_le = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    
    # Team status field
    STATUT_EQUIPE_CHOICES = [
        ('actif', 'Actif'),
        ('inactif', 'Inactif'),
        ('vacances', 'En vacances'),
        ('maladie', 'En arrêt maladie'),
        ('formation', 'En formation'),
    ]
    
    statut_equipe = models.CharField(
        max_length=20,
        choices=STATUT_EQUIPE_CHOICES,
        default='actif',
        verbose_name="Statut équipe",
        help_text="Statut actuel de l'utilisateur dans l'équipe"
    )
    
    # New field for warehouse-specific permissions
    acces_tous_entrepots = models.BooleanField(
        default=False, 
        verbose_name="Accès à tous les entrepôts",
        help_text="Si activé, l'utilisateur a accès à tous les entrepôts. Si désactivé, vous devez spécifier les entrepôts individuels ci-dessous."
    )

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        db_table = 'utilisateurs' # Nom de la table en base de données

    def __str__(self):
        return self.nom
    
    def get_team_role(self):
        """
        Returns the user's team role based on their groups
        """
        if self.user.is_superuser:
            return "Super Administrateur"
        
        groups = self.user.groups.all()
        if groups:
            return ", ".join([group.name for group in groups])
        return "Aucun rôle assigné"
    
    def get_accessible_warehouses(self):
        """
        Returns the warehouses this user has access to
        """
        from warehouse.models import Entrepot
        
        if self.acces_tous_entrepots:
            return Entrepot.objects.all()
        else:
            # Return Entrepot objects through the relationship
            return Entrepot.objects.filter(utilisateurs_autorises__utilisateur=self).distinct()
    
    def has_warehouse_access(self, entrepot):
        """
        Check if user has access to a specific warehouse
        """
        if self.acces_tous_entrepots:
            return True
        return self.entrepots_autorises.filter(entrepot=entrepot).exists()
    
    def has_warehouse_read_access(self, entrepot):
        """
        Check if user has read access to a specific warehouse
        """
        if self.acces_tous_entrepots:
            return True
        return self.entrepots_autorises.filter(entrepot=entrepot, peut_lire=True).exists()
    
    def has_warehouse_write_access(self, entrepot):
        """
        Check if user has write access to a specific warehouse
        """
        if self.acces_tous_entrepots:
            return True
        return self.entrepots_autorises.filter(entrepot=entrepot, peut_modifier=True).exists()
    
    def has_warehouse_delete_access(self, entrepot):
        """
        Check if user has delete access to a specific warehouse
        """
        if self.acces_tous_entrepots:
            return True
        return self.entrepots_autorises.filter(entrepot=entrepot, peut_supprimer=True).exists()


class UtilisateurEntrepot(models.Model):
    """
    Model to link users to specific warehouses they have access to
    """
    utilisateur = models.ForeignKey(
        Utilisateur, 
        on_delete=models.CASCADE, 
        related_name='entrepots_autorises',
        verbose_name="Utilisateur"
    )
    entrepot = models.ForeignKey(
        'warehouse.Entrepot', 
        on_delete=models.CASCADE,
        related_name='utilisateurs_autorises',
        verbose_name="Entrepôt"
    )
    
    # Simple boolean permissions instead of JSON
    peut_lire = models.BooleanField(
        default=True,
        verbose_name="Peut lire",
        help_text="L'utilisateur peut voir les données de cet entrepôt"
    )
    peut_modifier = models.BooleanField(
        default=False,
        verbose_name="Peut modifier",
        help_text="L'utilisateur peut modifier les données de cet entrepôt"
    )
    peut_supprimer = models.BooleanField(
        default=False,
        verbose_name="Peut supprimer",
        help_text="L'utilisateur peut supprimer les données de cet entrepôt"
    )
    
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Accès Utilisateur-Entrepôt"
        verbose_name_plural = "Accès Utilisateur-Entrepôt"
        db_table = 'utilisateur_entrepot'
        unique_together = ('utilisateur', 'entrepot')
    
    def __str__(self):
        return f"{self.utilisateur.nom} - {self.entrepot.nom}"
    
    @property
    def permissions_summary(self):
        """
        Returns a summary of permissions as a string
        """
        perms = []
        if self.peut_lire:
            perms.append("Lecture")
        if self.peut_modifier:
            perms.append("Modification")
        if self.peut_supprimer:
            perms.append("Suppression")
        return ", ".join(perms) if perms else "Aucune permission"
