from django.urls import path
from .views import lista_proyectos, detalle_proyecto

urlpatterns = [
    path('lista_proyectos/', lista_proyectos, name='lista_proyectos'),
    path('proyecto/<int:proyecto_id>/', detalle_proyecto, name='detalle_proyecto'),
]