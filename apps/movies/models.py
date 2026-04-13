from django.db import models

class Genero(models.Model):
    id_genero = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'generos'
        managed = False  # Usa la tabla provista

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
    genero = models.ForeignKey(Genero, models.DO_NOTHING, db_column='id_genero', blank=True, null=True)
    director = models.ForeignKey(Director, models.DO_NOTHING, db_column='id_director', blank=True, null=True)
    resumen = models.TextField(blank=True, null=True)
    imagen_url = models.CharField(max_length=500, blank=True, null=True)
    
    actores = models.ManyToManyField(Actor, through='PeliculaActor')
    plataformas = models.ManyToManyField(Plataforma, through='PeliculaPlataforma')

    class Meta:
        db_table = 'peliculas'
        managed = False

    def __str__(self):
        return self.nombre

class PeliculaActor(models.Model):
    pelicula = models.ForeignKey(Pelicula, models.DO_NOTHING, db_column='id_pelicula', primary_key=True)
    actor = models.ForeignKey(Actor, models.DO_NOTHING, db_column='id_actor')

    class Meta:
        db_table = 'pelicula_actor'
        managed = False
        unique_together = (('pelicula', 'actor'),)

class PeliculaPlataforma(models.Model):
    pelicula = models.ForeignKey(Pelicula, models.DO_NOTHING, db_column='id_pelicula', primary_key=True)
    plataforma = models.ForeignKey(Plataforma, models.DO_NOTHING, db_column='id_plataforma')

    class Meta:
        db_table = 'pelicula_plataforma'
        managed = False
        unique_together = (('pelicula', 'plataforma'),)
