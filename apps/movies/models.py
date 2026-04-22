from django.db import models


class Genero(models.Model):
    id_genero = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'generos'
        managed = False

    def __str__(self):
        return self.nombre


class Director(models.Model):
    id_director = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)

    class Meta:
        db_table = 'directores'
        managed = False

    def __str__(self):
        return self.nombre


class Actor(models.Model):
    id_actor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    imagen_url = models.CharField(max_length=500, blank=True, null=True)
    biografia = models.TextField(blank=True, null=True)
    pais_origen = models.CharField(max_length=120, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'actores'
        managed = False

    def __str__(self):
        return self.nombre

class Plataforma(models.Model):
    id_plataforma = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    url = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'plataformas'
        managed = False

    def __str__(self):
        return self.nombre


class Pelicula(models.Model):
    id_pelicula = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    anio = models.IntegerField(db_column='anio', verbose_name='Año')
    resumen = models.TextField(blank=True, null=True)
    imagen_url = models.CharField(max_length=500, blank=True, null=True)

    generos = models.ManyToManyField(
        Genero,
        through='PeliculaGenero',
        related_name='peliculas'
    )

    directores = models.ManyToManyField(
        Director,
        through='PeliculaDirector',
        related_name='peliculas'
    )

    actores = models.ManyToManyField(
        Actor,
        through='PeliculaActor',
        related_name='peliculas'
    )

    plataformas = models.ManyToManyField(
        Plataforma,
        through='PeliculaPlataforma',
        related_name='peliculas'
    )

    class Meta:
        db_table = 'peliculas'
        managed = False

    def __str__(self):
        return self.nombre

    def generos_display(self):
        nombres = list(self.generos.values_list('nombre', flat=True))
        return ", ".join(nombres[:3]) if nombres else "Sin género"

    def directores_display(self):
        nombres = list(self.directores.values_list('nombre', flat=True))
        return ", ".join(nombres[:3]) if nombres else "Sin director"


class PeliculaGenero(models.Model):
    id = models.AutoField(primary_key=True)
    pelicula = models.ForeignKey(Pelicula, models.DO_NOTHING, db_column='id_pelicula')
    genero = models.ForeignKey(Genero, models.DO_NOTHING, db_column='id_genero')

    class Meta:
        db_table = 'pelicula_genero'
        managed = False
        unique_together = (('pelicula', 'genero'),)


class PeliculaDirector(models.Model):
    id = models.AutoField(primary_key=True)
    pelicula = models.ForeignKey(Pelicula, models.DO_NOTHING, db_column='id_pelicula')
    director = models.ForeignKey(Director, models.DO_NOTHING, db_column='id_director')

    class Meta:
        db_table = 'pelicula_director'
        managed = False
        unique_together = (('pelicula', 'director'),)


class PeliculaActor(models.Model):
    id = models.AutoField(primary_key=True)
    pelicula = models.ForeignKey(Pelicula, models.DO_NOTHING, db_column='id_pelicula')
    actor = models.ForeignKey(Actor, models.DO_NOTHING, db_column='id_actor')

    class Meta:
        db_table = 'pelicula_actor'
        managed = False
        unique_together = (('pelicula', 'actor'),)


class PeliculaPlataforma(models.Model):
    id = models.AutoField(primary_key=True)
    pelicula = models.ForeignKey(Pelicula, models.DO_NOTHING, db_column='id_pelicula')
    plataforma = models.ForeignKey(Plataforma, models.DO_NOTHING, db_column='id_plataforma')

    class Meta:
        db_table = 'pelicula_plataforma'
        managed = False
        unique_together = (('pelicula', 'plataforma'),)