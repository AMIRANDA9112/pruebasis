from django.urls import path
from . import views

from django.contrib import admin
urlpatterns = [

    path('conjuntos/', views.conjuntos, name='conjuntos'),
    path('admin/', admin.site.urls),
    path('conjuntos_json/', views.conjuntos_json, name='conjuntos_json'),
    path('dimensiones_json/<int:conjunto_id>/', views.dimensiones_json, name='dimensiones_json'),
    path('tematicas_json/<int:dimension_id>/', views.tematicas_json, name='tematicas_json'),
    path('indicadores_json/<int:tematica_id>/', views.indicadores_json, name='indicadores_json'),
    path('datos_json/<int:indicador_id>/', views.datos_json, name='datos_json'),
    path('', views.home, name='home'),
    path('sistemas/', views.sistemas, name='sistemas'),
    path('temas/', views.temas, name='temas'),
    path('poblacion/', views.poblacion, name='poblacion'),
]
