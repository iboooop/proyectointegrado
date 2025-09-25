from django.db import models

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación
    updated_at = models.DateTimeField(auto_now=True)      # Fecha de última actualización

    class Meta:
        abstract = True  # Esto indica que esta clase no se creará como tabla en la base de datos
