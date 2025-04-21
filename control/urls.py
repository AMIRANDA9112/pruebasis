from django.urls import path
from . import views

app_name = 'control'

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/usuario/', views.dashboard_usuario, name='dashboard_usuario'),
    
    # Gestión de usuarios
    path('crear-usuario/', views.crear_usuario, name='crear_usuario'),
    path('editar-usuario/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('ver-usuarios/', views.ver_usuarios, name='ver_usuarios'),
    
    # Gestión de bases de datos
    path('subir-base-datos/', views.subir_base_datos, name='subir_base_datos'),
    path('ver-bases-datos/', views.ver_bases_datos, name='ver_bases_datos'),
    
    # Gestión de permisos
    path('ver-permisos/', views.ver_permisos, name='ver_permisos'),
    path('asignar-permisos/<int:base_id>/', views.asignar_permisos, name='asignar_permisos'),
    path('editar-permiso/<int:permiso_id>/', views.editar_permiso, name='editar_permiso'),
    
    # Visualización de datos
    path('ver-base-datos/<int:base_id>/', views.ver_base_datos, name='ver_base_datos'),
    path('ver-usuarios/<int:base_id>/', views.ver_usuarios_base, name='ver_usuarios_base'),
    path('ver-permisos-usuario/<int:usuario_id>/', views.ver_permisos_usuario, name='ver_permisos_usuario'),
]
