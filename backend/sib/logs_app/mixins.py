from .utils import log_activity

class LoggingMixin:
    """
    A mixin for Django REST Framework ViewSets to automatically log CRUD operations.
    """
    def perform_create(self, serializer):
        instance = serializer.save()
        if self.request.user.is_authenticated:
            log_activity(
                user=self.request.user,
                action=f"Création de {instance._meta.verbose_name}",
                entity=instance,
                details=f"Nouvel enregistrement créé: {instance}"
            )

    def perform_update(self, serializer):
        # old_instance = self.get_object() # You could get old data here for diffing if needed
        instance = serializer.save()
        if self.request.user.is_authenticated:
            log_activity(
                user=self.request.user,
                action=f"Mise à jour de {instance._meta.verbose_name}",
                entity=instance,
                details=f"Enregistrement mis à jour: {instance}"
            )

    def perform_destroy(self, instance):
        if self.request.user.is_authenticated:
            log_activity(
                user=self.request.user,
                action=f"Suppression de {instance._meta.verbose_name}",
                entity=instance,
                details=f"Enregistrement supprimé: {instance}"
            )
        instance.delete()
