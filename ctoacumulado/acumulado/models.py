# data_app/models.py
from django.db import models

# Definición de modelos para las tablas existentes
# Todas las tablas tienen la misma estructura de columnas:
# id (PK), codmaq (VARCHAR(50)), valor (VARCHAR(20)), t_stamp (TIMESTAMP)

class Seriada062025(models.Model): # Cambiado de HaySeriada062025 a Seriada062025
    id = models.AutoField(primary_key=True)
    codmaq = models.CharField(max_length=50, blank=True, null=True)
    valor = models.CharField(max_length=20, blank=True, null=True)
    t_stamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'seriada_06_2025' # Asegúrate que este nombre de tabla coincida exactamente
        verbose_name = 'Dato Seriada'
        verbose_name_plural = 'Datos Seriada' # Correcto

    def __str__(self):
        return f"ID: {self.id} - CodMaq: {self.codmaq} - Valor: {self.valor} - Fecha: {self.t_stamp}"

class Llaves062025(models.Model):
    id = models.AutoField(primary_key=True)
    codmaq = models.CharField(max_length=50, blank=True, null=True)
    valor = models.CharField(max_length=20, blank=True, null=True)
    t_stamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'llaves_06_2025'
        verbose_name = 'Dato de Llaves'
        verbose_name_plural = 'Datos de Llaves' # ¡CORREGIDO AQUÍ!
        # Era verbose_plural, ahora es verbose_name_plural

    def __str__(self):
        return f"ID: {self.id} - CodMaq: {self.codmaq} - Valor: {self.valor} - Fecha: {self.t_stamp}"

class Forja062025(models.Model):
    id = models.AutoField(primary_key=True)
    codmaq = models.CharField(max_length=50, blank=True, null=True)
    valor = models.CharField(max_length=20, blank=True, null=True)
    t_stamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'forja_06_2025'
        verbose_name = 'Dato de Forja'
        verbose_name_plural = 'Datos de Forja'

    def __str__(self):
        return f"ID: {self.id} - CodMaq: {self.codmaq} - Valor: {self.valor} - Fecha: {self.t_stamp}"

class Maestranza062025(models.Model):
    id = models.AutoField(primary_key=True)
    codmaq = models.CharField(max_length=50, blank=True, null=True)
    valor = models.CharField(max_length=20, blank=True, null=True)
    t_stamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'maestranza_06_2025'
        verbose_name = 'Dato de Maestranza'
        verbose_name_plural = 'Datos de Maestranza'

    def __str__(self):
        return f"ID: {self.id} - CodMaq: {self.codmaq} - Valor: {self.valor} - Fecha: {self.t_stamp}"

# MES JULIO
class Seriada072025(models.Model):
    id = models.AutoField(primary_key=True)
    codmaq = models.CharField(max_length=50, blank=True, null=True)
    valor = models.CharField(max_length=20, blank=True, null=True)
    t_stamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'seriada_07_2025'
        verbose_name = 'Dato Seriada'
        verbose_name_plural = 'Datos Seriada'

    def __str__(self):
        return f"ID: {self.id} - CodMaq: {self.codmaq} - Valor: {self.valor} - Fecha: {self.t_stamp}"

class Llaves072025(models.Model):
    id = models.AutoField(primary_key=True)
    codmaq = models.CharField(max_length=50, blank=True, null=True)
    valor = models.CharField(max_length=20, blank=True, null=True)
    t_stamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'llaves_07_2025'
        verbose_name = 'Dato de Llaves'
        verbose_name_plural = 'Datos de Llaves'

    def __str__(self):
        return f"ID: {self.id} - CodMaq: {self.codmaq} - Valor: {self.valor} - Fecha: {self.t_stamp}"

class Forja072025(models.Model):
    id = models.AutoField(primary_key=True)
    codmaq = models.CharField(max_length=50, blank=True, null=True)
    valor = models.CharField(max_length=20, blank=True, null=True)
    t_stamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'forja_07_2025'
        verbose_name = 'Dato de Forja'
        verbose_name_plural = 'Datos de Forja'

    def __str__(self):
        return f"ID: {self.id} - CodMaq: {self.codmaq} - Valor: {self.valor} - Fecha: {self.t_stamp}"

class Maestranza072025(models.Model):
    id = models.AutoField(primary_key=True)
    codmaq = models.CharField(max_length=50, blank=True, null=True)
    valor = models.CharField(max_length=20, blank=True, null=True)
    t_stamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'maestranza_07_2025'
        verbose_name = 'Dato de Maestranza'
        verbose_name_plural = 'Datos de Maestranza'

    def __str__(self):
        return f"ID: {self.id} - CodMaq: {self.codmaq} - Valor: {self.valor} - Fecha: {self.t_stamp}"