from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    id_usuario = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def can_interact(self):
        from django.utils import timezone
        today = timezone.now().date()
        return self.suscripcion_set.filter(
            plan__precio__gt=0,
            fecha_inicio__lte=today,
            fecha_fin__gte=today
        ).exists()

    @property
    def current_plan_name(self):
        from django.utils import timezone
        today = timezone.now().date()
        suscripcion = self.suscripcion_set.filter(
            fecha_inicio__lte=today,
            fecha_fin__gte=today
        ).order_by('-plan__precio').first()

        if suscripcion:
            return suscripcion.plan.nombre
        return "Gratuita"

    @property
    def current_plan_id(self):
        from django.utils import timezone
        today = timezone.now().date()
        suscripcion = self.suscripcion_set.filter(
            fecha_inicio__lte=today,
            fecha_fin__gte=today
        ).order_by('-plan__precio').first()

        if suscripcion:
            return suscripcion.plan.id_plan
        return None

    class Meta:
        db_table = 'usuarios'
        managed = True

    def __str__(self):
        return self.email


class Plan(models.Model):
    id_plan = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    duracion_meses = models.IntegerField()

    class Meta:
        db_table = 'planes'
        managed = False

    def __str__(self):
        return self.nombre


class Suscripcion(models.Model):
    id_suscripcion = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    plan = models.ForeignKey(Plan, models.DO_NOTHING, db_column='id_plan', blank=True, null=True)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'suscripciones'
        managed = False


class MetodoPago(models.Model):
    id_pago = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='id_usuario', blank=True, null=True)
    numero_tarjeta = models.CharField(max_length=20)
    nombre_tarjeta = models.CharField(max_length=150)
    fecha_expiracion = models.DateField()
    cvv = models.CharField(max_length=4)

    class Meta:
        db_table = 'metodo_pago'
        managed = False

class UsuarioGeneroPreferencia(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        Usuario,
        models.DO_NOTHING,
        db_column='id_usuario',
        related_name='preferencias_genero'
    )
    genero = models.ForeignKey(
        'movies.Genero',
        models.DO_NOTHING,
        db_column='id_genero',
        related_name='usuarios_preferidos'
    )

    class Meta:
        db_table = 'usuario_genero_preferencia'
        managed = False
        unique_together = (('usuario', 'genero'),)

    def __str__(self):
        return f"{self.usuario.email} - {self.genero.nombre}"