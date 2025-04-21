from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator

class CustomUser(AbstractUser):
    """Modelo personalizado para usuarios"""
    TIPO_USUARIO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('CONTROLADO', 'Acceso Controlado')
    ]
    
    tipo_usuario = models.CharField(
        max_length=10, 
        choices=TIPO_USUARIO_CHOICES,
        default='CONTROLADO',
        null=False,
        blank=False
    )
    
    # Sobrescribir las relaciones para evitar conflictos
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    def __str__(self):
        return self.username

class UsuarioControlado(models.Model):
    """Modelo para usuarios con acceso controlado"""
    usuario = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    correo = models.EmailField(unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    documento = models.CharField(max_length=20, unique=True)
    entidad = models.CharField(max_length=200)
    cargo = models.CharField(max_length=100)
    acuerdo_confidencialidad = models.FileField(
        upload_to='acuerdos_confidencialidad/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.entidad}"

class BaseDatos(models.Model):
    """Modelo para almacenar las bases de datos CSV"""
    nombre = models.CharField(max_length=200)
    archivo = models.FileField(upload_to='bases_datos/', validators=[FileExtensionValidator(allowed_extensions=['csv'])])
    descripcion = models.TextField(blank=True, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    subido_por = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='bases_subidas'
    )
    
    def __str__(self):
        return self.nombre

class PermisoBaseDatos(models.Model):
    """Modelo para controlar los permisos de acceso a las bases de datos"""
    usuario = models.ForeignKey(UsuarioControlado, on_delete=models.CASCADE)
    base_datos = models.ForeignKey(BaseDatos, on_delete=models.CASCADE)
    puede_descargar = models.BooleanField(default=False)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('usuario', 'base_datos')
    
    def __str__(self):
        return f"{self.usuario} - {self.base_datos}"

class LogAcceso(models.Model):
    """Modelo para registrar los logs de acceso a bases de datos"""
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    base_datos = models.ForeignKey(BaseDatos, on_delete=models.CASCADE)
    fecha_acceso = models.DateTimeField(auto_now_add=True)
    accion = models.CharField(max_length=50)  # 'VISUALIZAR', 'DESCARGAR'
    
    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.fecha_acceso}"
