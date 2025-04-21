from django.db import models
from django.contrib.gis.db import models as geomodels

class Proyecto(models.Model):
    nombre = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.nombre

class Ciudadano(models.Model):
    nombre = models.CharField(max_length=200)
    edad = models.IntegerField()
    ingresos_anuales = models.DecimalField(max_digits=12, decimal_places=2)
    genero = models.CharField(max_length=20)
    # Relación: cada ciudadano puede estar asociado a un proyecto y a un predio
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="ciudadanos", null=True, blank=True)
    predio = models.ForeignKey('Predio', on_delete=models.SET_NULL, related_name="ciudadanos", null=True, blank=True)

    def __str__(self):
        return self.nombre

# Modelo para los barrios (cargados desde geojson)
class Barrio(geomodels.Model):
    numero = models.IntegerField(verbose_name="Número de barrio")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del barrio")
    comuna = models.CharField(max_length=100)
    geom = geomodels.PolygonField()

    def __str__(self):
        return self.nombre

# Modelo para los predios (cargados desde geojson)
class Predio(geomodels.Model):
    numero_unico = models.CharField(max_length=50, unique=True, verbose_name="Número único del predio")
    direccion = models.CharField(max_length=255, null=True, blank=True)
    geom = geomodels.MultiPolygonField()
    # Relación: cada predio pertenece a un barrio
    barrio = models.ForeignKey(Barrio, on_delete=models.SET_NULL, related_name="predios", null=True, blank=True)

    def __str__(self):
        return self.numero_unico
