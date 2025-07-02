from django.db import models

# Create your models here.
class CircutorDataDia(models.Model): # Cambiado de HaySeriada062025 a Seriada062025
    fecha = models.DateField()
    valor = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'circutor_dia_2025_06' # Asegúrate que este nombre de tabla coincida exactamente
        verbose_name = 'Dato Circutor'
        verbose_name_plural = 'Datos Circutor' # Correcto

    def __str__(self):
        return f"fecha: {self.fecha} - valor: {self.valor}"