from django.contrib import admin
from .models import Pelicula, Genero, Director, Actor, Plataforma, PeliculaActor, PeliculaPlataforma

@admin.register(Pelicula)
class PeliculaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'anio', 'genero', 'director')
    search_fields = ('nombre',)
    list_filter = ('genero', 'anio')

@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)

admin.site.register(Actor)
admin.site.register(Plataforma)
admin.site.register(PeliculaActor)
admin.site.register(PeliculaPlataforma)
