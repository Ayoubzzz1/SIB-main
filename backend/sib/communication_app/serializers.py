from rest_framework import serializers
from .models import Message
from users_app.serializers import UtilisateurSerializer

class MessageSerializer(serializers.ModelSerializer):
    id_expediteur_details = UtilisateurSerializer(source='id_expediteur', read_only=True)
    id_destinataire_details = UtilisateurSerializer(source='id_destinataire', read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'id_expediteur', 'id_expediteur_details', 'id_destinataire', 'id_destinataire_details', 'message', 'cree_le', 'statut_lu')
        read_only_fields = ('id', 'cree_le', 'id_expediteur_details', 'id_destinataire_details')
        extra_kwargs = {
            'id_expediteur': {'write_only': True, 'required': False} # L'expéditeur sera défini automatiquement
        }

    def create(self, validated_data):
        # Définir l'expéditeur automatiquement à partir de l'utilisateur authentifié
        if self.context['request'].user.is_authenticated and hasattr(self.context['request'].user, 'utilisateur'):
            validated_data['id_expediteur'] = self.context['request'].user.utilisateur
        else:
            raise serializers.ValidationError("L'expéditeur doit être un utilisateur authentifié.")
        return super().create(validated_data)
