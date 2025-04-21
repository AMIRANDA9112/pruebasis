from django.contrib import admin
from .models import ConjuntoIndicadores, Dimension, Tematica, Indicador, SerieDatos, Dato, Comuna

admin.site.register(ConjuntoIndicadores)
admin.site.register(Dimension)
admin.site.register(Tematica)
admin.site.register(Indicador)
admin.site.register(SerieDatos)
admin.site.register(Dato)
admin.site.register(Comuna)

