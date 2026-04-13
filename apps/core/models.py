from django.db import models

class BaseModel(models.Model):
    """
    Modelo base abstracto que provee atributos comunes
    como fecha de creación y de actualización para otros modelos.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
