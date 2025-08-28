"""
Signals for automatic logging in inventory app
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Stock, MouvementStock, MatierePremiere, ProduitFini, ProduitSemiFini
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

# Stock logging
@receiver(post_save, sender=Stock)
def log_stock_changes(sender, instance, created, **kwargs):
    """Log stock changes"""
    if created:
        create_log_entry("Création", instance, f"Stock créé: {instance.quantite} unités")
    else:
        create_log_entry("Modification", instance, f"Stock modifié: {instance.quantite} unités")

@receiver(post_delete, sender=Stock)
def log_stock_deletion(sender, instance, **kwargs):
    """Log stock deletion"""
    create_log_entry("Suppression", instance, f"Stock supprimé: {instance.quantite} unités")

# Stock movement logging
@receiver(post_save, sender=MouvementStock)
def log_stock_movement(sender, instance, created, **kwargs):
    """Log stock movements"""
    if created:
        create_log_entry("Mouvement", instance, 
                        f"Mouvement de stock: {instance.type_mouvement} - {instance.quantite} unités")

# Raw materials logging
@receiver(post_save, sender=MatierePremiere)
def log_matiere_premiere_changes(sender, instance, created, **kwargs):
    """Log raw material changes"""
    if created:
        create_log_entry("Création", instance, f"Matière première '{instance.nom}' créée")
    else:
        create_log_entry("Modification", instance, f"Matière première '{instance.nom}' modifiée")

@receiver(post_delete, sender=MatierePremiere)
def log_matiere_premiere_deletion(sender, instance, **kwargs):
    """Log raw material deletion"""
    create_log_entry("Suppression", instance, f"Matière première '{instance.nom}' supprimée")

# Finished products logging
@receiver(post_save, sender=ProduitFini)
def log_produit_fini_changes(sender, instance, created, **kwargs):
    """Log finished product changes"""
    if created:
        create_log_entry("Création", instance, f"Produit fini '{instance.nom}' créé")
    else:
        create_log_entry("Modification", instance, f"Produit fini '{instance.nom}' modifié")

@receiver(post_delete, sender=ProduitFini)
def log_produit_fini_deletion(sender, instance, **kwargs):
    """Log finished product deletion"""
    create_log_entry("Suppression", instance, f"Produit fini '{instance.nom}' supprimé")

# Semi-finished products logging
@receiver(post_save, sender=ProduitSemiFini)
def log_produit_semi_fini_changes(sender, instance, created, **kwargs):
    """Log semi-finished product changes"""
    if created:
        create_log_entry("Création", instance, f"Produit semi-fini '{instance.nom}' créé")
    else:
        create_log_entry("Modification", instance, f"Produit semi-fini '{instance.nom}' modifié")

@receiver(post_delete, sender=ProduitSemiFini)
def log_produit_semi_fini_deletion(sender, instance, **kwargs):
    """Log semi-finished product deletion"""
    create_log_entry("Suppression", instance, f"Produit semi-fini '{instance.nom}' supprimé")
