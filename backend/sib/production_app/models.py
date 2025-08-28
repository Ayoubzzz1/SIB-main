from django.db import models
from django.core.exceptions import ValidationError
from users_app.models import Utilisateur
from inventory_app.models import MatierePremiere, ProduitSemiFini, ProduitFini
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Production(models.Model):
    STATUT_CHOICES = [
        ('planifiee', 'Planifiée'),
        ('en_cours', 'En Cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ]

    # Polymorphic FK for id_produit (either semi-finished or finished product)
    produit_semi_fini = models.ForeignKey(
        ProduitSemiFini,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordres_production_semi_fini',
        verbose_name="Produit Semi-Fini à Produire"
    )
    produit_fini = models.ForeignKey(
        ProduitFini,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordres_production_fini',
        verbose_name="Produit Fini à Produire"
    )

    quantite_prevue = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantité Prévue")
    quantite_produite = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Quantité Produite")
    date_debut = models.DateField(verbose_name="Date de Début")
    date_fin = models.DateField(blank=True, null=True, verbose_name="Date de Fin")
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='planifiee', verbose_name="Statut")
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='ordres_production_crees', verbose_name="Créé par")
    cree_le = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Ordre de Production"
        verbose_name_plural = "Ordres de Production"
        db_table = 'production'

    def clean(self):
        # Ensure only one of produit_semi_fini or produit_fini is set
        if self.produit_semi_fini and self.produit_fini:
            raise ValidationError("Un ordre de production ne peut concerner qu'un seul type de produit (semi-fini ou fini).")
        if not self.produit_semi_fini and not self.produit_fini:
            raise ValidationError("Un ordre de production doit concerner un produit semi-fini ou un produit fini.")

    def __str__(self):
        if self.produit_semi_fini:
            return f"Production de {self.produit_semi_fini.nom} (Quantité: {self.quantite_prevue})"
        elif self.produit_fini:
            return f"Production de {self.produit_fini.nom} (Quantité: {self.quantite_prevue})"
        return f"Ordre de Production #{self.id}"

class MatiereProduction(models.Model):
    id_production = models.ForeignKey(Production, on_delete=models.CASCADE, related_name='matieres_utilisee', verbose_name="Ordre de Production")
    id_matiere = models.ForeignKey(MatierePremiere, on_delete=models.CASCADE, related_name='utilisations_production', verbose_name="Matière Première")
    quantite_utilisee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantité Utilisée")

    class Meta:
        verbose_name = "Matière Utilisée en Production"
        verbose_name_plural = "Matières Utilisées en Production"
        db_table = 'matieres_production'
        unique_together = ('id_production', 'id_matiere') # Une matière ne peut être listée qu'une fois par ordre de production

    def __str__(self):
        return f"{self.quantite_utilisee} {self.id_matiere.unite} de {self.id_matiere.nom} pour Production #{self.id_production.id}"

class NomenclatureProduits(models.Model):
    TYPE_PRODUIT_PARENT_CHOICES = [
        ('semi_fini', 'Produit Semi-Fini'),
        ('fini', 'Produit Fini'),
    ]
    TYPE_COMPOSANT_CHOICES = [
        ('matiere', 'Matière Première'),
        ('semi_fini', 'Produit Semi-Fini'),
    ]

    # Generic Foreign Key for parent_product_id
    content_type_parent = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='nomenclature_produits_parent'
    )
    id_produit_parent = models.PositiveIntegerField(verbose_name="ID Produit Parent")
    produit_parent = GenericForeignKey('content_type_parent', 'id_produit_parent')
    type_produit_parent = models.CharField(max_length=50, choices=TYPE_PRODUIT_PARENT_CHOICES, verbose_name="Type Produit Parent")

    # Generic Foreign Key for component_item_id
    content_type_composant = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='nomenclature_produits_composant'
    )
    id_composant = models.PositiveIntegerField(verbose_name="ID Composant")
    composant = GenericForeignKey('content_type_composant', 'id_composant')
    type_composant = models.CharField(max_length=50, choices=TYPE_COMPOSANT_CHOICES, verbose_name="Type Composant")

    quantite_requise = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantité Requise")
    unite = models.CharField(max_length=50, verbose_name="Unité")
    cree_le = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Nomenclature Produit"
        verbose_name_plural = "Nomenclatures Produits"
        db_table = 'nomenclature_produits'
        unique_together = (
            'content_type_parent', 'id_produit_parent',
            'content_type_composant', 'id_composant'
        )

    def __str__(self):
        return f"Pour {self.produit_parent} : {self.quantite_requise} {self.unite} de {self.composant}"
