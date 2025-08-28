from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import MatierePremiere, ProduitSemiFini, ProduitFini, Stock, MouvementStock
from warehouse.models import Entrepot
from users_app.models import Utilisateur

class MatierePremiereSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatierePremiere
        fields = '__all__'
        read_only_fields = ('id', 'cree_le')

class ProduitSemiFiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProduitSemiFini
        fields = '__all__'
        read_only_fields = ('id', 'cree_le')

class ProduitFiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProduitFini
        fields = '__all__'
        read_only_fields = ('id', 'cree_le')

class MouvementStockSerializer(serializers.ModelSerializer):
    article_nom = serializers.SerializerMethodField(read_only=True)
    type_article = serializers.CharField(write_only=True, required=False)
    content_type = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all(),
        write_only=True,
        required=False
    )
    id_article = serializers.IntegerField(write_only=True, required=False)
    entrepot_nom = serializers.CharField(source='entrepot.nom', read_only=True)
    entrepot_source_nom = serializers.CharField(source='entrepot_source.nom', read_only=True)
    utilisateur_nom = serializers.CharField(source='utilisateur.nom', read_only=True)
    
    # Computed fields for source and destination
    source_nom_computed = serializers.SerializerMethodField()
    destination_nom_computed = serializers.SerializerMethodField()

    class Meta:
        model = MouvementStock
        fields = (
            'id', 'type_mouvement', 'motif', 'type_article', 'content_type', 'id_article', 
            'article_nom', 'quantite', 'entrepot', 'entrepot_nom', 'entrepot_source', 
            'entrepot_source_nom', 'utilisateur', 'utilisateur_nom', 'source_type', 
            'source_nom', 'source_nom_computed', 'fournisseur_source', 'entrepot_source_fk', 
            'destination_type', 'destination_nom', 'destination_nom_computed', 
            'client_destination', 'entrepot_destination_fk', 'reference', 
            'commentaire', 'date_mouvement'
        )
        read_only_fields = ('id', 'date_mouvement', 'article_nom', 'entrepot_nom', 'entrepot_source_nom', 'utilisateur_nom')

    def get_article_nom(self, obj):
        if obj.article:
            return str(obj.article)
        return None

    def get_source_nom_computed(self, obj):
        """Get the computed source name based on source_type"""
        if obj.source_type == 'fournisseur' and obj.fournisseur_source:
            return f"{obj.fournisseur_source.code_fournisseur} - {obj.fournisseur_source.nom_entreprise}"
        elif obj.source_type == 'entrepot' and obj.entrepot_source_fk:
            return obj.entrepot_source_fk.nom
        elif obj.source_nom:
            return obj.source_nom
        return None

    def get_destination_nom_computed(self, obj):
        """Get the computed destination name based on destination_type"""
        if obj.destination_type == 'client' and obj.client_destination:
            return obj.client_destination.nom_entreprise
        elif obj.destination_type == 'entrepot' and obj.entrepot_destination_fk:
            return obj.entrepot_destination_fk.nom
        elif obj.destination_nom:
            return obj.destination_nom
        return None

    def validate(self, data):
        # For creation, check required fields
        if self.instance is None:  # Creation
            if not data.get('content_type'):
                raise serializers.ValidationError({"content_type": "Le type de contenu est requis."})
            if not data.get('id_article'):
                raise serializers.ValidationError({"id_article": "L'ID de l'article est requis."})
            if not data.get('entrepot'):
                raise serializers.ValidationError({"entrepot": "L'entrepôt est requis."})
            # Note: utilisateur will be set automatically in perform_create
            
            # For transfers, entrepot_source is required
            if data.get('type_mouvement') == 'transfert' and not data.get('entrepot_source'):
                raise serializers.ValidationError({"entrepot_source": "L'entrepôt source est requis pour un transfert."})
            
            # For transfers, entrepot and entrepot_source must be different
            if data.get('type_mouvement') == 'transfert' and data.get('entrepot') == data.get('entrepot_source'):
                raise serializers.ValidationError("L'entrepôt source et l'entrepôt destination doivent être différents.")
        
        return data

    def create(self, validated_data):
        content_type = validated_data.pop('content_type')
        id_article = validated_data.pop('id_article')
        type_article = validated_data.pop('type_article', None)
        
        # Verify the article exists
        try:
            article = content_type.get_object_for_this_type(id=id_article)
        except content_type.model_class().DoesNotExist:
            raise serializers.ValidationError(f"L'article avec l'ID {id_article} n'existe pas pour le type {content_type.model}.")
        
        # Create the movement
        mouvement = MouvementStock.objects.create(
            content_type=content_type,
            id_article=id_article,
            **validated_data
        )
        
        # Update stock quantity
        stock, created = Stock.objects.get_or_create(
            content_type=content_type,
            id_article=id_article,
            entrepot=validated_data['entrepot'],
            defaults={'type_article': type_article or self._get_type_article_from_content_type(content_type)}
        )
        stock.mettre_a_jour_quantite()
        
        # For transfers, also update source warehouse stock
        if validated_data.get('type_mouvement') == 'transfert' and validated_data.get('entrepot_source'):
            stock_source, created_source = Stock.objects.get_or_create(
                content_type=content_type,
                id_article=id_article,
                entrepot=validated_data['entrepot_source'],
                defaults={'type_article': type_article or self._get_type_article_from_content_type(content_type)}
            )
            stock_source.mettre_a_jour_quantite()
        
        return mouvement

    def _get_type_article_from_content_type(self, content_type):
        """Get type_article from content_type model name"""
        model_name = content_type.model
        if model_name == 'matierepremiere':
            return 'matiere'
        elif model_name == 'produitsemifini':
            return 'semi_fini'
        elif model_name == 'produitfini':
            return 'fini'
        return 'matiere'  # default

class StockSerializer(serializers.ModelSerializer):
    article_nom = serializers.SerializerMethodField(read_only=True)
    type_article = serializers.CharField(required=False)  # Make it not required for updates
    content_type = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all(),
        write_only=True,
        required=False
    )
    id_article = serializers.IntegerField(write_only=True, required=False)
    entrepot = serializers.PrimaryKeyRelatedField(
        queryset=Entrepot.objects.all(),
        required=False
    )
    entrepot_nom = serializers.CharField(source='entrepot.nom', read_only=True)
    quantite_disponible = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Stock
        fields = ('id', 'type_article', 'content_type', 'id_article', 'article_nom', 'quantite', 'quantite_disponible', 'entrepot', 'entrepot_nom', 'derniere_maj')
        read_only_fields = ('id', 'derniere_maj', 'article_nom', 'entrepot_nom', 'quantite_disponible')

    def get_article_nom(self, obj):
        if obj.article:
            return str(obj.article)
        return None

    def get_quantite_disponible(self, obj):
        """Calculate and return available quantity"""
        return obj.calculer_quantite_disponible()

    def validate(self, data):
        # Pour la création, vérifier que les champs requis sont présents
        if self.instance is None:  # Création
            if not data.get('content_type'):
                raise serializers.ValidationError({"content_type": "Le type de contenu est requis pour la création."})
            if not data.get('id_article'):
                raise serializers.ValidationError({"id_article": "L'ID de l'article est requis pour la création."})
            if not data.get('entrepot'):
                raise serializers.ValidationError({"entrepot": "L'entrepôt est requis pour la création."})
            if not data.get('type_article'):
                raise serializers.ValidationError({"type_article": "Le type d'article est requis pour la création."})
        return data

    def create(self, validated_data):
        content_type = validated_data.pop('content_type')
        id_article = validated_data.pop('id_article')
        entrepot = validated_data.pop('entrepot')
        
        if not content_type or not id_article:
            raise serializers.ValidationError("Le type de contenu et l'ID de l'article sont requis pour la création.")
            
        try:
            obj = content_type.get_object_for_this_type(id=id_article)
        except content_type.model_class().DoesNotExist:
            raise serializers.ValidationError(f"L'article avec l'ID {id_article} n'existe pas pour le type {content_type.model}.")
        model_name = content_type.model
        if model_name == 'matierepremiere' and validated_data['type_article'] != 'matiere':
            raise serializers.ValidationError("Le type d'article doit être 'matiere' pour une MatierePremiere.")
        elif model_name == 'produitsemifini' and validated_data['type_article'] != 'semi_fini':
            raise serializers.ValidationError("Le type d'article doit être 'semi_fini' pour un ProduitSemiFini.")
        elif model_name == 'produitfini' and validated_data['type_article'] != 'fini':
            raise serializers.ValidationError("Le type d'article doit être 'fini' pour un ProduitFini.")
        return Stock.objects.create(content_type=content_type, id_article=id_article, entrepot=entrepot, **validated_data)

    def update(self, instance, validated_data):
        # Supprimer les champs qui ne doivent pas être modifiés
        validated_data.pop('content_type', None)
        validated_data.pop('id_article', None)
        validated_data.pop('type_article', None)
        
        # Mettre à jour l'entrepôt si fourni
        if 'entrepot' in validated_data:
            instance.entrepot = validated_data['entrepot']
            validated_data.pop('entrepot')
        
        # Mettre à jour la quantité si fournie
        if 'quantite' in validated_data:
            instance.quantite = validated_data['quantite']
            validated_data.pop('quantite')
        
        instance.save()
        return instance
