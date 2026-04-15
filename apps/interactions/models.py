from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
from apps.movies.models import Pelicula

class Favorite(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    movie = models.ForeignKey(Pelicula, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.user.username} - Favorito: {self.movie.nombre}"

class Watchlist(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watchlist')
    movie = models.ForeignKey(Pelicula, on_delete=models.CASCADE, related_name='watchlist_users')
    watched = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.user.username} - Watchlist: {self.movie.nombre}"

class HistorialVisita(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='id_usuario',
        related_name='historial_visitas'
    )
    pelicula = models.ForeignKey(
        Pelicula,
        on_delete=models.CASCADE,
        db_column='id_pelicula',
        related_name='visitas_usuario'
    )
    fecha_visita = models.DateTimeField()

    class Meta:
        db_table = 'historial_visitas'
        managed = False

    def __str__(self):
        return f"{self.usuario.username} vio {self.pelicula.nombre}"