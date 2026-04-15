from django.contrib import admin
from .models import Favorite, Watchlist, HistorialVisita


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie')
    search_fields = ('user__username', 'user__email', 'movie__nombre')


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'watched')
    search_fields = ('user__username', 'user__email', 'movie__nombre')


@admin.register(HistorialVisita)
class HistorialVisitaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'pelicula', 'fecha_visita')
    search_fields = ('usuario__username', 'usuario__email', 'pelicula__nombre')
    list_filter = ('fecha_visita',)