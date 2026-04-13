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
