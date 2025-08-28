from django.db import models
from users_app.models import Utilisateur
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class HistoriqueActivite(models.Model):
    id_utilisateur = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, related_name='activites', verbose_name="Utilisateur")
    action = models.CharField(max_length=255, verbose_name="Action")
    
    # Generic Foreign Key for entity_id
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    id_entite = models.PositiveIntegerField(verbose_name="ID Entité")
    entite_affectee = GenericForeignKey('content_type', 'id_entite')

    horodatage = models.DateTimeField(auto_now_add=True, verbose_name="Horodatage")
    details = models.TextField(blank=True, verbose_name="Détails")

    class Meta:
        verbose_name = "Historique d'Activité"
        verbose_name_plural = "Historiques d'Activités"
        db_table = 'historique_activites'
        ordering = ['-horodatage'] # Order by newest first

    def __str__(self):
        user_name = self.id_utilisateur.nom if self.id_utilisateur else "Utilisateur Inconnu"
        return f"{user_name} a effectué '{self.action}' sur {self.entite_affectee} le {self.horodatage.strftime('%Y-%m-%d %H:%M')}"
