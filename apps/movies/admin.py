from django.contrib import admin
from .models import (
    Pelicula,
    Genero,
    Director,
    Actor,
    Plataforma,
    PeliculaGenero,
    PeliculaDirector,
    PeliculaActor,
    PeliculaPlataforma,
)


class PeliculaGeneroInline(admin.TabularInline):
    model = PeliculaGenero
    extra = 1
    autocomplete_fields = ['genero']


class PeliculaDirectorInline(admin.TabularInline):
    model = PeliculaDirector
    extra = 1
    autocomplete_fields = ['director']


class PeliculaActorInline(admin.TabularInline):
    model = PeliculaActor
    extra = 1
    autocomplete_fields = ['actor']


class PeliculaPlataformaInline(admin.TabularInline):
    model = PeliculaPlataforma
    extra = 1
    autocomplete_fields = ['plataforma']


@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Plataforma)
class PlataformaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'url')
    search_fields = ('nombre',)


@admin.register(Pelicula)
class PeliculaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'anio', 'generos_admin', 'directores_admin')
    search_fields = ('nombre', 'generos__nombre', 'directores__nombre')
    list_filter = ('anio',)
    inlines = [
        PeliculaGeneroInline,
        PeliculaDirectorInline,
        PeliculaActorInline,
        PeliculaPlataformaInline,
    ]

    def generos_admin(self, obj):
        return obj.generos_display()
    generos_admin.short_description = 'Géneros'

    def directores_admin(self, obj):
        return obj.directores_display()
    directores_admin.short_description = 'Directores'


@admin.register(PeliculaGenero)
class PeliculaGeneroAdmin(admin.ModelAdmin):
    list_display = ('pelicula', 'genero')
    search_fields = ('pelicula__nombre', 'genero__nombre')
    autocomplete_fields = ['pelicula', 'genero']


@admin.register(PeliculaDirector)
class PeliculaDirectorAdmin(admin.ModelAdmin):
    list_display = ('pelicula', 'director')
    search_fields = ('pelicula__nombre', 'director__nombre')
    autocomplete_fields = ['pelicula', 'director']


@admin.register(PeliculaActor)
class PeliculaActorAdmin(admin.ModelAdmin):
    list_display = ('pelicula', 'actor')
    search_fields = ('pelicula__nombre', 'actor__nombre')
    autocomplete_fields = ['pelicula', 'actor']


@admin.register(PeliculaPlataforma)
class PeliculaPlataformaAdmin(admin.ModelAdmin):
    list_display = ('pelicula', 'plataforma')
    search_fields = ('pelicula__nombre', 'plataforma__nombre')
    autocomplete_fields = ['pelicula', 'plataforma']