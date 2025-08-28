from django.db import models

# Create your models here.

class Entrepot(models.Model):
    nom = models.CharField(max_length=255, verbose_name="Nom de l'entrepôt")
    adresse = models.CharField(max_length=255, blank=True, verbose_name="Adresse")
    description = models.TextField(blank=True, verbose_name="Description")
    cree_le = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Entrepôt"
        verbose_name_plural = "Entrepôts"
        db_table = 'entrepots'

    def __str__(self):
        return self.nom
