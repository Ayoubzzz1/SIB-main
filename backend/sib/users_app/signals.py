from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import Utilisateur

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Only create Utilisateur profile if one doesn't already exist
        # This prevents conflicts when creating users through the API
        try:
            instance.utilisateur
        except Utilisateur.DoesNotExist:
            # For new users, create a default Utilisateur profile
            # You might want to set a default role like 'commercial' or 'magasin'
            # or even add a new 'default' role if users are created without specific roles.
            # For now, let's default to 'commercial' for new users created outside admin.
            Utilisateur.objects.create(user=instance, nom=instance.username)
        
        # Assign user to default group if they don't have any groups
        if not instance.groups.exists() and not instance.is_superuser:
            try:
                default_group = Group.objects.get(name='Commerciaux')
                instance.groups.add(default_group)
            except Group.DoesNotExist:
                # If default group doesn't exist, don't fail - just log it
                pass
    else:
        # For existing users, create profile if it doesn't exist
        try:
            instance.utilisateur
        except Utilisateur.DoesNotExist:
            Utilisateur.objects.create(
                user=instance, 
                nom=instance.username
            )
