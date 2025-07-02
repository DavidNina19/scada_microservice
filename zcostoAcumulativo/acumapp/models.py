from django.db import models

# Create your models here.
class CircutorData(models.Model): # Cambiado de HaySeriada062025 a Seriada062025
    id = models.AutoField(primary_key=True)
    area = models.CharField(max_length=50, blank=True, null=True)
    valor = models.CharField(max_length=20, blank=True, null=True)
    t_stamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'circutor_data_2025_06' # Asegúrate que este nombre de tabla coincida exactamente
        verbose_name = 'Dato Circutor'
        verbose_name_plural = 'Datos Circutor' # Correcto

    def __str__(self):
        return f"ID: {self.id} - Area: {self.area} - Valor: {self.valor} - Fecha: {self.t_stamp}"