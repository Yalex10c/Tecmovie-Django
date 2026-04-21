from django.db import models
from django.conf import settings
from apps.movies.models import Pelicula


class Resena(models.Model):
    id_resena = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    pelicula = models.ForeignKey(
        Pelicula,
        models.DO_NOTHING,
        db_column='id_pelicula',
        blank=True,
        null=True,
        related_name='resenas'
    )
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        db_table = 'resenas'
        managed = False


class Calificacion(models.Model):
    id_calificacion = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    pelicula = models.ForeignKey(Pelicula, models.DO_NOTHING, db_column='id_pelicula', blank=True, null=True)
    reaccion = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        db_table = 'calificaciones'
        managed = False
        unique_together = (('usuario', 'pelicula'),)

    def __str__(self):
        return f"{self.usuario} - {self.pelicula} - {self.reaccion}"