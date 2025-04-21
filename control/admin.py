from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UsuarioControlado, BaseDatos, PermisoBaseDatos, LogAcceso

# Personalizar la visualización de CustomUser en el admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'tipo_usuario', 'is_staff')
    list_filter = ('tipo_usuario', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'tipo_usuario')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'tipo_usuario')}
        ),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

# Personalizar la visualización de UsuarioControlado en el admin
class UsuarioControladoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'correo', 'nombres', 'apellidos', 'entidad')
    list_filter = ('entidad',)
    search_fields = ('usuario__username', 'correo', 'nombres', 'apellidos', 'entidad')
    readonly_fields = ('fecha_creacion',)

# Personalizar la visualización de BaseDatos en el admin
class BaseDatosAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'fecha_subida')
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('fecha_subida',)

# Personalizar la visualización de PermisoBaseDatos en el admin
class PermisoBaseDatosAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'base_datos', 'puede_descargar', 'fecha_asignacion')
    list_filter = ('puede_descargar', 'fecha_asignacion')
    search_fields = ('usuario__usuario__username', 'base_datos__nombre')
    readonly_fields = ('fecha_asignacion',)

# Personalizar la visualización de LogAcceso en el admin
class LogAccesoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'base_datos', 'fecha_acceso', 'accion')
    list_filter = ('fecha_acceso', 'accion')
    search_fields = ('usuario__username', 'base_datos__nombre')
    readonly_fields = ('fecha_acceso',)

# Registrar los modelos
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UsuarioControlado, UsuarioControladoAdmin)
admin.site.register(BaseDatos, BaseDatosAdmin)
admin.site.register(PermisoBaseDatos, PermisoBaseDatosAdmin)
admin.site.register(LogAcceso, LogAccesoAdmin)

# Personalizar el título del sitio
admin.site.site_header = "Administración de Control de Datos"
admin.site.site_title = "Control de Datos"
admin.site.index_title = "Panel de Administración"
