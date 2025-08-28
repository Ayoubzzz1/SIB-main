from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Production, MatiereProduction, NomenclatureProduits
from users_app.serializers import UtilisateurSerializer

# Importez les MODÈLES eux-mêmes pour les querysets des PrimaryKeyRelatedField
from inventory_app.models import MatierePremiere, ProduitSemiFini, ProduitFini

# Importez les SÉRIALISEURS pour les représentations imbriquées, en utilisant des alias
from inventory_app.serializers import (
    MatierePremiereSerializer as InventoryMatierePremiereSerializer,
    ProduitSemiFiniSerializer as InventoryProduitSemiFiniSerializer,
    ProduitFiniSerializer as InventoryProduitFiniSerializer,
)

class ProductionSerializer(serializers.ModelSerializer):
    cree_par_details = UtilisateurSerializer(source='cree_par', read_only=True)
    
    # Pour la lecture, afficher le nom du produit à produire
    produit_a_produire_nom = serializers.SerializerMethodField(read_only=True)

    # Pour l'écriture, permettre de spécifier l'ID du produit semi-fini ou fini
    produit_semi_fini = serializers.PrimaryKeyRelatedField(
        queryset=ProduitSemiFini.objects.all(), required=False, allow_null=True
    )
    produit_fini = serializers.PrimaryKeyRelatedField(
        queryset=ProduitFini.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Production
        fields = (
            'id', 'produit_semi_fini', 'produit_fini', 'produit_a_produire_nom',
            'quantite_prevue', 'quantite_produite', 'date_debut', 'date_fin',
            'statut', 'cree_par', 'cree_par_details', 'cree_le'
        )
        read_only_fields = ('id', 'cree_le', 'cree_par_details', 'produit_a_produire_nom')

    def get_produit_a_produire_nom(self, obj):
        if obj.produit_semi_fini:
            return str(obj.produit_semi_fini)
        elif obj.produit_fini:
            return str(obj.produit_fini)
        return None

    def validate(self, data):
        produit_semi_fini = data.get('produit_semi_fini')
        produit_fini = data.get('produit_fini')

        if produit_semi_fini and produit_fini:
            raise serializers.ValidationError("Un ordre de production ne peut concerner qu'un seul type de produit (semi-fini ou fini).")
        if not produit_semi_fini and not produit_fini:
            raise serializers.ValidationError("Un ordre de production doit concerner un produit semi-fini ou un produit fini.")
        return data

    def create(self, validated_data):
        if self.context['request'].user.is_authenticated and hasattr(self.context['request'].user, 'utilisateur'):
            validated_data['cree_par'] = self.context['request'].user.utilisateur
        return super().create(validated_data)

class MatiereProductionSerializer(serializers.ModelSerializer):
    id_matiere_details = InventoryMatierePremiereSerializer(source='id_matiere', read_only=True)

    class Meta:
        model = MatiereProduction
        fields = ('id', 'id_production', 'id_matiere', 'id_matiere_details', 'quantite_utilisee')
        read_only_fields = ('id',)
        extra_kwargs = {
            'id_production': {'write_only': True} # L'ID de production est généralement défini par la vue parente
        }

class NomenclatureProduitsSerializer(serializers.ModelSerializer):
    # Pour la lecture, afficher les noms des objets liés
    produit_parent_nom = serializers.SerializerMethodField(read_only=True)
    composant_nom = serializers.SerializerMethodField(read_only=True)

    # Pour l'écriture, permettre de spécifier les IDs et ContentTypes
    content_type_parent = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all(), write_only=True, required=True
    )
    id_produit_parent = serializers.IntegerField(write_only=True, required=True)
    content_type_composant = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all(), write_only=True, required=True
    )
    id_composant = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = NomenclatureProduits
        fields = (
            'id', 'content_type_parent', 'id_produit_parent', 'produit_parent_nom', 'type_produit_parent',
            'content_type_composant', 'id_composant', 'composant_nom', 'type_composant',
            'quantite_requise', 'unite', 'cree_le'
        )
        read_only_fields = ('id', 'cree_le', 'produit_parent_nom', 'composant_nom')

    def get_produit_parent_nom(self, obj):
        if obj.produit_parent:
            return str(obj.produit_parent)
        return None

    def get_composant_nom(self, obj):
        if obj.composant:
            return str(obj.composant)
        return None

    def create(self, validated_data):
        content_type_parent = validated_data.pop('content_type_parent')
        id_produit_parent = validated_data.pop('id_produit_parent')
        content_type_composant = validated_data.pop('content_type_composant')
        id_composant = validated_data.pop('id_composant')

        # Vérifier que les IDs correspondent aux ContentTypes
        try:
            parent_obj = content_type_parent.get_object_for_this_type(id=id_produit_parent)
        except content_type_parent.model_class().DoesNotExist:
            raise serializers.ValidationError(f"Le produit parent avec l'ID {id_produit_parent} n'existe pas pour le type {content_type_parent.model}.")
        
        try:
            composant_obj = content_type_composant.get_object_for_this_type(id=id_composant)
        except content_type_composant.model_class().DoesNotExist:
            raise serializers.ValidationError(f"Le composant avec l'ID {id_composant} n'existe pas pour le type {content_type_composant.model}.")

        # Assurez-vous que les types correspondent aux modèles
        if content_type_parent.model == 'produitsemifini' and validated_data['type_produit_parent'] != 'semi_fini':
            raise serializers.ValidationError("Le type de produit parent doit être 'semi_fini' pour un ProduitSemiFini.")
        elif content_type_parent.model == 'produitfini' and validated_data['type_produit_parent'] != 'fini':
            raise serializers.ValidationError("Le type de produit parent doit être 'fini' pour un ProduitFini.")

        if content_type_composant.model == 'matierepremiere' and validated_data['type_composant'] != 'matiere':
            raise serializers.ValidationError("Le type de composant doit être 'matiere' pour une MatierePremiere.")
        elif content_type_composant.model == 'produitsemifini' and validated_data['type_composant'] != 'semi_fini':
            raise serializers.ValidationError("Le type de composant doit être 'semi_fini' pour un ProduitSemiFini.")

        return NomenclatureProduits.objects.create(
            content_type_parent=content_type_parent, id_produit_parent=id_produit_parent,
            content_type_composant=content_type_composant, id_composant=id_composant,
            **validated_data
        )

    def update(self, instance, validated_data):
        # Empêcher la modification des clés génériques après la création
        if 'content_type_parent' in validated_data or 'id_produit_parent' in validated_data or \
           'content_type_composant' in validated_data or 'id_composant' in validated_data:
            raise serializers.ValidationError("Les références d'article parent et de composant ne peuvent pas être modifiées après la création.")
        return super().update(instance, validated_data)
