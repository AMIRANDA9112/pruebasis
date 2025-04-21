import django.contrib.gis.db as geo
from django.db import models

class Comuna(models.Model):
    """
    Modelo para representar una comuna.
    """
    comuna_id = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255)
    area = models.FloatField()
    perimetro = models.FloatField()
    geom = geo.models.PolygonField()  # Campo para la geometría del polígono

    def __str__(self):
        return self.nombre


    def indicadores_comuna(self):
        """
        Obtiene los indicadores relacionados con la comuna a través de las series de datos.
        """
        return Indicador.objects.filter(seriedatos__desagregacion_geografica=self.nombre).distinct()

    def datos_comuna(self):
        """
        Obtiene los datos más recientes para cada serie de datos relacionada con la comuna.
        """
        indicadores = self.indicadores_comuna()
        datos = []
        for indicador in indicadores:
            series_datos = SerieDatos.objects.filter(indicador=indicador, desagregacion_geografica=self.nombre)
            for serie in series_datos:
                # Obtener el dato más reciente para la serie
                dato_reciente = Dato.objects.filter(serie_datos=serie).order_by('-fecha_dato').first()
                if dato_reciente:
                    datos.append({
                        'indicador_nombre': indicador.descripcion,
                        'serie_datos_nombre': serie.nombre,
                        'fecha_dato': dato_reciente.fecha_dato.strftime('%Y'),
                        'valor_dato': float(dato_reciente.valor_dato),
                        'unidad_medida': serie.unidad_medida,
                    })
        return datos

class ConjuntoIndicadores(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Dimension(models.Model):
    conjunto = models.ForeignKey(ConjuntoIndicadores, on_delete=models.CASCADE) # Agregar relación con ConjuntoIndicadores
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Tematica(models.Model):
    dimension = models.ForeignKey(Dimension, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Indicador(models.Model):
    tematica = models.ForeignKey(Tematica, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class SerieDatos(models.Model):
    nombre = models.CharField(max_length=255, blank=True, null=True)
    indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE)
    tipo_desagregacion_geografica = models.CharField(max_length=255, blank=True, null=True)
    desagregacion_geografica = models.CharField(max_length=255, blank=True, null=True)
    periodicidad = models.CharField(max_length=255, blank=True, null=True)
    entidad_recopilatoria = models.CharField(max_length=255, blank=True, null=True)
    fuente_datos = models.CharField(max_length=255, blank=True, null=True)
    desagregacion_tematica = models.CharField(max_length=255, blank=True, null=True)
    unidad_medida = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nombre

class Dato(models.Model):
    nombre = models.CharField(max_length=255, blank=True, null=True)
    serie_datos = models.ForeignKey(SerieDatos, on_delete=models.CASCADE)
    fecha_dato = models.DateField()
    valor_dato = models.DecimalField(max_digits=20, decimal_places=2)
    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre
