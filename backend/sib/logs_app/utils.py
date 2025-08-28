from django.contrib.contenttypes.models import ContentType
from .models import HistoriqueActivite
from users_app.models import Utilisateur
from django.core.exceptions import ObjectDoesNotExist # Import this

def log_activity(user, action, entity, details=''):
    """
    Logs an activity in the HistoriqueActivite model.
    :param user: The Django User instance performing the action.
    :param action: A string describing the action (e.g., "Création", "Mise à jour", "Suppression").
    :param entity: The model instance (e.g., MatierePremiere, Commande) that was affected.
    :param details: Optional additional details about the action.
    """
    if user and user.is_authenticated:
        try:
            utilisateur_profile = user.utilisateur # Attempt to get the linked profile
        except ObjectDoesNotExist:
            # If no Utilisateur profile is linked, log a warning and skip logging this activity
            print(f"Warning: User '{user.username}' (ID: {user.id}) does not have a linked Utilisateur profile. Activity '{action}' on {entity} not logged.")
            return # Exit the function if profile is missing

        content_type = ContentType.objects.get_for_model(entity)
        HistoriqueActivite.objects.create(
            id_utilisateur=utilisateur_profile,
            action=action,
            content_type=content_type,
            id_entite=entity.pk,
            details=details
        )
    else:
        print(f"Warning: Attempted to log activity for unauthenticated user. Activity '{action}' on {entity} not logged.")
