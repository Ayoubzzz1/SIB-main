from rest_framework import serializers
from .models import HistoriqueActivite
from users_app.serializers import UtilisateurSerializer
from django.contrib.contenttypes.models import ContentType

class HistoriqueActiviteSerializer(serializers.ModelSerializer):
    id_utilisateur_details = UtilisateurSerializer(source='id_utilisateur', read_only=True)
    
    # For reading, display the name of the affected entity
    entite_affectee_nom = serializers.SerializerMethodField(read_only=True)
    # Add a field to show the model name of the content type
    type_entite_nom = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = HistoriqueActivite
        fields = ('id', 'id_utilisateur', 'id_utilisateur_details', 'action', 'type_entite_nom', 'id_entite', 'entite_affectee_nom', 'horodatage', 'details')
        # Removed read_only_fields = '__all__' as it causes issues with DRF

    def get_entite_affectee_nom(self, obj):
        if obj.entite_affectee:
            return str(obj.entite_affectee)
        return None

    def get_type_entite_nom(self, obj):
        # Return the model name of the content type
        return obj.content_type.model if obj.content_type else None
