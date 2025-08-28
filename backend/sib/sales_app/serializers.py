from rest_framework import serializers
from .models import Client, Commande, ArticleCommande, Fournisseur
from decimal import Decimal
from users_app.serializers import UtilisateurSerializer # Pour afficher les détails de l'utilisateur créateur
from inventory_app.serializers import ProduitFiniSerializer # Pour afficher les détails du produit fini

class FournisseurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fournisseur
        fields = '__all__'
        read_only_fields = ('id', 'cree_le')

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ('id', 'cree_le')

class ArticleCommandeSerializer(serializers.ModelSerializer):
    id_produit_details = ProduitFiniSerializer(source='id_produit', read_only=True) # Détails du produit
    id_commande_details = serializers.SerializerMethodField() # Détails de la commande
    
    class Meta:
        model = ArticleCommande
        fields = ('id', 'id_commande', 'id_commande_details', 'id_produit', 'id_produit_details', 'quantite', 'prix_unitaire')
        read_only_fields = ('id', 'id_commande_details', 'id_produit_details')

    def get_id_commande_details(self, obj):
        if obj.id_commande:
            return {
                'id': obj.id_commande.id,
                'client': obj.id_commande.id_client.nom_entreprise if obj.id_commande.id_client else None,
                'reference': f"CMD-{obj.id_commande.id}"
            }
        return None

class CommandeSerializer(serializers.ModelSerializer):
    articles = ArticleCommandeSerializer(many=True, read_only=True) # Affiche les articles de la commande
    cree_par_details = UtilisateurSerializer(source='cree_par', read_only=True) # Détails de l'utilisateur créateur
    id_client_details = ClientSerializer(source='id_client', read_only=True) # Détails du client
    # Computed fields for frontend convenience
    total = serializers.SerializerMethodField()
    reference = serializers.SerializerMethodField()
    client = serializers.SerializerMethodField()

    class Meta:
        model = Commande
        fields = (
            'id', 'id_client', 'id_client_details', 'client', 'reference', 'total',
            'statut', 'date_commande', 'date_livraison', 'cree_par', 'cree_par_details', 'cree_le', 'articles'
        )
        read_only_fields = ('id', 'cree_le', 'cree_par_details', 'id_client_details', 'client', 'reference', 'total', 'articles')

    def get_total(self, obj: Commande):
        total = Decimal('0')
        for art in obj.articles.all():
            total += (art.quantite * art.prix_unitaire)
        return float(total)

    def get_reference(self, obj: Commande):
        return f"CMD-{obj.id}"

    def get_client(self, obj: Commande):
        return obj.id_client.nom_entreprise if obj.id_client else None
