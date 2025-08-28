from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from warehouse.models import Entrepot
from users_app.models import Utilisateur

class MatierePremiere(models.Model):
    nom = models.CharField(max_length=255, verbose_name="Nom")
    code_reference = models.CharField(max_length=100, unique=True, verbose_name="Code de Référence")
    unite = models.CharField(max_length=50, verbose_name="Unité")
    description = models.TextField(blank=True, verbose_name="Description")
    niveau_min_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Niveau Min. Stock")
    est_archive = models.BooleanField(default=False, verbose_name="Est Archivé")
    cree_le = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Matière Première"
        verbose_name_plural = "Matières Premières"
        db_table = 'matieres_premieres'

    def __str__(self):
        return self.nom

class ProduitSemiFini(models.Model):
    nom = models.CharField(max_length=255, verbose_name="Nom")
    code_reference = models.CharField(max_length=100, unique=True, verbose_name="Code de Référence")
    unite = models.CharField(max_length=50, verbose_name="Unité")
    description = models.TextField(blank=True, verbose_name="Description")
    niveau_min_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Niveau Min. Stock")
    est_archive = models.BooleanField(default=False, verbose_name="Est Archivé")
    cree_le = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Produit Semi-Fini"
        verbose_name_plural = "Produits Semi-Finis"
        db_table = 'produits_semi_finis'

    def __str__(self):
        return self.nom

class ProduitFini(models.Model):
    nom = models.CharField(max_length=255, verbose_name="Nom")
    code_reference = models.CharField(max_length=100, unique=True, verbose_name="Code de Référence")
    unite = models.CharField(max_length=50, verbose_name="Unité")
    description = models.TextField(blank=True, verbose_name="Description")
    niveau_min_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Niveau Min. Stock")
    est_archive = models.BooleanField(default=False, verbose_name="Est Archivé")
    cree_le = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Produit Fini"
        verbose_name_plural = "Produits Finis"
        db_table = 'produits_finis'

    def __str__(self):
        return self.nom

class MouvementStock(models.Model):
    TYPE_MOUVEMENT_CHOICES = [
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
        ('ajustement', 'Ajustement'),
        ('transfert', 'Transfert'),
    ]

    MOTIF_CHOICES = [
        ('reception', 'Réception'),
        ('vente', 'Vente'),
        ('production', 'Production'),
        ('perte', 'Perte'),
        ('ajustement', 'Ajustement'),
        ('transfert', 'Transfert'),
        ('autre', 'Autre'),
    ]

    SOURCE_TYPE_CHOICES = [
        ('fournisseur', 'Fournisseur'),
        ('entrepot', 'Entrepôt'),
    ]

    DESTINATION_TYPE_CHOICES = [
        ('client', 'Client'),
        ('entrepot', 'Entrepôt'),
    ]

    type_mouvement = models.CharField(max_length=20, choices=TYPE_MOUVEMENT_CHOICES, verbose_name="Type de Mouvement")
    motif = models.CharField(max_length=20, choices=MOTIF_CHOICES, verbose_name="Motif")
    
    # Generic Foreign Key for item
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name="Type de Contenu")
    id_article = models.PositiveIntegerField(verbose_name="ID Article")
    article = GenericForeignKey('content_type', 'id_article')

    quantite = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantité")
    entrepot = models.ForeignKey(Entrepot, on_delete=models.PROTECT, verbose_name="Entrepôt")
    
    # User who made the movement
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.PROTECT, verbose_name="Utilisateur")
    
    # Source/Destination tracking
    source_type = models.CharField(
        max_length=20, 
        choices=SOURCE_TYPE_CHOICES, 
        blank=True, 
        null=True,
        verbose_name="Type de Source"
    )
    source_nom = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name="Nom de la Source"
    )
    # Foreign Key relationships for better data integrity
    fournisseur_source = models.ForeignKey(
        'sales_app.Fournisseur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mouvements_fournisseur',
        verbose_name="Fournisseur Source"
    )
    entrepot_source_fk = models.ForeignKey(
        'warehouse.Entrepot',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mouvements_source_entrepot',
        verbose_name="Entrepôt Source"
    )
    client_destination = models.ForeignKey(
        'sales_app.Client',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mouvements_client',
        verbose_name="Client Destination"
    )
    entrepot_destination_fk = models.ForeignKey(
        'warehouse.Entrepot',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mouvements_destination_entrepot',
        verbose_name="Entrepôt Destination"
    )
    destination_type = models.CharField(
        max_length=20, 
        choices=DESTINATION_TYPE_CHOICES, 
        blank=True, 
        null=True,
        verbose_name="Type de Destination"
    )
    destination_nom = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name="Nom de la Destination"
    )
    
    # Reference fields
    reference = models.CharField(max_length=100, blank=True, verbose_name="Référence")
    commentaire = models.TextField(blank=True, verbose_name="Commentaire")
    
    # Timestamps
    date_mouvement = models.DateTimeField(auto_now_add=True, verbose_name="Date du Mouvement")
    
    # For transfers, track source and destination warehouses
    entrepot_source = models.ForeignKey(
        Entrepot, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True, 
        related_name='mouvements_source',
        verbose_name="Entrepôt Source"
    )

    class Meta:
        verbose_name = "Mouvement de Stock"
        verbose_name_plural = "Mouvements de Stock"
        db_table = 'mouvements_stock'
        ordering = ['-date_mouvement']

    def __str__(self):
        return f"{self.get_type_mouvement_display()} - {self.article} ({self.quantite}) - {self.entrepot.nom}"

    def save(self, *args, **kwargs):
        # Auto-set entrepot_source for transfers
        if self.type_mouvement == 'transfert' and not self.entrepot_source:
            # This should be set by the API when creating transfers
            pass
        super().save(*args, **kwargs)

class Stock(models.Model):
    TYPE_ARTICLE_CHOICES = [
        ('matiere', 'Matière Première'),
        ('semi_fini', 'Produit Semi-Fini'),
        ('fini', 'Produit Fini'),
    ]

    type_article = models.CharField(max_length=50, choices=TYPE_ARTICLE_CHOICES, verbose_name="Type d'Article")
    
    # Generic Foreign Key for item_id
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    id_article = models.PositiveIntegerField(verbose_name="ID Article")
    article = GenericForeignKey('content_type', 'id_article')

    quantite = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantité", default=0)
    entrepot = models.ForeignKey(Entrepot, on_delete=models.PROTECT, verbose_name="Entrepôt")
    derniere_maj = models.DateTimeField(auto_now=True, verbose_name="Dernière Mise à Jour")

    class Meta:
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"
        db_table = 'stock'
        # Ensure unique stock entry per item and location
        unique_together = ('content_type', 'id_article', 'entrepot')

    def __str__(self):
        return f"{self.article} ({self.quantite} {self.article.unite if hasattr(self.article, 'unite') else ''}) à {self.entrepot.nom}"

    def calculer_quantite_disponible(self):
        """Calculate available quantity based on movements"""
        mouvements = MouvementStock.objects.filter(
            content_type=self.content_type,
            id_article=self.id_article,
            entrepot=self.entrepot
        )
        
        total_entrees = mouvements.filter(type_mouvement='entree').aggregate(
            total=models.Sum('quantite')
        )['total'] or 0
        
        total_sorties = mouvements.filter(type_mouvement='sortie').aggregate(
            total=models.Sum('quantite')
        )['total'] or 0
        
        total_ajustements = mouvements.filter(type_mouvement='ajustement').aggregate(
            total=models.Sum('quantite')
        )['total'] or 0
        
        # For transfers, add entries and subtract exits
        transferts_entrees = mouvements.filter(
            type_mouvement='transfert',
            entrepot=self.entrepot
        ).aggregate(total=models.Sum('quantite'))['total'] or 0
        
        transferts_sorties = mouvements.filter(
            type_mouvement='transfert',
            entrepot_source=self.entrepot
        ).aggregate(total=models.Sum('quantite'))['total'] or 0
        
        return total_entrees - total_sorties + total_ajustements + transferts_entrees - transferts_sorties

    def mettre_a_jour_quantite(self):
        """Update quantity based on movements"""
        self.quantite = self.calculer_quantite_disponible()
        self.save(update_fields=['quantite', 'derniere_maj'])
