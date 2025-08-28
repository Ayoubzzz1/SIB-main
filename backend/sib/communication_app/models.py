from django.db import models
from users_app.models import Utilisateur

class Message(models.Model):
    id_expediteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='messages_envoyes', verbose_name="Expéditeur")
    id_destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='messages_recus', verbose_name="Destinataire")
    message = models.TextField(verbose_name="Message")
    cree_le = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    statut_lu = models.BooleanField(default=False, verbose_name="Statut Lu")

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        db_table = 'messages'
        ordering = ['-cree_le'] # Order by newest first

    def __str__(self):
        return f"De {self.id_expediteur.nom} à {self.id_destinataire.nom} - {self.message[:50]}..."
