from django.db import models
from django.conf import settings
from apps.movies.models import Pelicula

class Resena(models.Model):
    id_resena = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    pelicula = models.ForeignKey(Pelicula, models.DO_NOTHING, db_column='id_pelicula', blank=True, null=True)
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        db_table = 'resenas'
        managed = False

class Calificacion(models.Model):
    id_calificacion = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    pelicula = models.ForeignKey(Pelicula, models.DO_NOTHING, db_column='id_pelicula', blank=True, null=True)
    puntuacion = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)

    class Meta:
        db_table = 'calificaciones'
        managed = False
