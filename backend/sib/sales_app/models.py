from django.db import models
from users_app.models import Utilisateur
from inventory_app.models import ProduitFini

class Fournisseur(models.Model):
    nom_entreprise = models.CharField(max_length=255, verbose_name="Nom de l'Entreprise")
    personne_contact = models.CharField(max_length=255, blank=True, verbose_name="Personne de Contact")
    email = models.EmailField(blank=True, verbose_name="Email")
    telephone = models.CharField(max_length=50, blank=True, verbose_name="Téléphone")
    adresse = models.TextField(blank=True, verbose_name="Adresse")
    code_fournisseur = models.CharField(max_length=50, unique=True, verbose_name="Code Fournisseur")
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    cree_le = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        db_table = 'fournisseurs'

    def __str__(self):
        return f"{self.code_fournisseur} - {self.nom_entreprise}"

class Client(models.Model):
    nom_entreprise = models.CharField(max_length=255, verbose_name="Nom de l'Entreprise")
    personne_contact = models.CharField(max_length=255, blank=True, verbose_name="Personne de Contact")
    email = models.EmailField(blank=True, verbose_name="Email")
    telephone = models.CharField(max_length=50, blank=True, verbose_name="Téléphone")
    adresse = models.TextField(blank=True, verbose_name="Adresse")
    cree_le = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        db_table = 'clients'

    def __str__(self):
        return self.nom_entreprise

class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En Attente'),
        ('en_production', 'En Production'),
        ('expediee', 'Expédiée'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]

    id_client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='commandes', verbose_name="Client")
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='en_attente', verbose_name="Statut")
    date_commande = models.DateField(verbose_name="Date de Commande")
    date_livraison = models.DateField(blank=True, null=True, verbose_name="Date de Livraison Prévue")
    cree_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='commandes_creees', verbose_name="Créée par")
    cree_le = models.DateTimeField(auto_now_add=True, verbose_name="Créée le")

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        db_table = 'commandes'

    def __str__(self):
        return f"Commande #{self.id} - {self.id_client.nom_entreprise}"

class ArticleCommande(models.Model):
    id_commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='articles', verbose_name="Commande")
    id_produit = models.ForeignKey(ProduitFini, on_delete=models.CASCADE, related_name='articles_commandes', verbose_name="Produit Fini")
    quantite = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantité")
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix Unitaire")

    class Meta:
        verbose_name = "Article de Commande"
        verbose_name_plural = "Articles de Commande"
        db_table = 'articles_commande'
        unique_together = ('id_commande', 'id_produit') # Un produit ne peut être qu'une fois par commande

    def __str__(self):
        return f"{self.quantite} x {self.id_produit.nom} pour Commande #{self.id_commande.id}"
