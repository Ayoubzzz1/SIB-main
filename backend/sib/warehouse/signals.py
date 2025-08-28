"""
Signals for automatic logging in warehouse app
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Entrepot
from logs_app.models import HistoriqueActivite

def get_current_user():
    """Get current user from request or default to system user"""
    try:
        from django.contrib.auth.models import User
        return User.objects.filter(is_superuser=True).first()
    except:
        return None

def create_log_entry(action, instance, details=None, user=None):
    """Create a log entry for an action"""
    try:
        if user is None:
            user = get_current_user()
        
        if user is None:
            return
        
        # Get content type
        content_type = ContentType.objects.get_for_model(instance.__class__)
        
        # Create log entry
        HistoriqueActivite.objects.create(
            action=action,
            id_utilisateur=user.utilisateur if hasattr(user, 'utilisateur') else None,
            content_type=content_type,
            id_entite=instance.id,
            details=details or f"{action} de {instance}"
        )
        
    except Exception as e:
        print(f"Error creating log entry: {e}")

@receiver(post_save, sender=Entrepot)
def log_entrepot_changes(sender, instance, created, **kwargs):
    """Log entrepôt changes"""
    if created:
        create_log_entry("Création", instance, f"Entrepôt '{instance.nom}' créé")
    else:
        create_log_entry("Modification", instance, f"Entrepôt '{instance.nom}' modifié")

@receiver(post_delete, sender=Entrepot)
def log_entrepot_deletion(sender, instance, **kwargs):
    """Log entrepôt deletion"""
    create_log_entry("Suppression", instance, f"Entrepôt '{instance.nom}' supprimé")
