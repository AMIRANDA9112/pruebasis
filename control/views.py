from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import PermissionDenied
import pandas as pd
from .models import CustomUser, UsuarioControlado, BaseDatos, PermisoBaseDatos, LogAcceso
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def dashboard_admin(request):
    """Dashboard para administradores"""
    # Verificar que el usuario es admin
    try:
        custom_user = CustomUser.objects.get(username=request.user.username)
        if not request.user.is_staff or custom_user.tipo_usuario != 'ADMIN':
            raise PermissionDenied("No tiene permisos para acceder a este dashboard")
    except CustomUser.DoesNotExist:
        raise PermissionDenied("Usuario no configurado correctamente")
    
    usuarios_controlados = UsuarioControlado.objects.all()
    bases_datos = BaseDatos.objects.all()
    
    return render(request, 'control/dashboard_admin.html', {
        'usuarios_controlados': usuarios_controlados,
        'bases_datos': bases_datos,
        'tipo_usuario': custom_user.tipo_usuario
    })

@login_required
def dashboard_usuario(request):
    """Dashboard para usuarios con acceso controlado"""
    # Verificar que el usuario es de tipo CONTROLADO
    try:
        custom_user = CustomUser.objects.get(username=request.user.username)
        if custom_user.tipo_usuario != 'CONTROLADO':
            raise PermissionDenied("No tiene permisos para acceder a este dashboard")
    except CustomUser.DoesNotExist:
        raise PermissionDenied("Usuario no configurado correctamente")
    
    try:
        # Obtener el usuario controlado asociado
        usuario_controlado = UsuarioControlado.objects.get(usuario=custom_user)
        
        # Obtener los permisos del usuario
        permisos = PermisoBaseDatos.objects.filter(usuario=usuario_controlado)
        
        # Crear una lista de bases de datos con información de permisos
        bases_datos = []
        for permiso in permisos:
            base_datos = permiso.base_datos
            bases_datos.append({
                'id': base_datos.id,
                'nombre': base_datos.nombre,
                'descripcion': base_datos.descripcion,
                'fecha_subida': base_datos.fecha_subida,
                'subido_por': base_datos.subido_por,
                'puede_descargar': permiso.puede_descargar
            })
        
        return render(request, 'control/dashboard_usuario.html', {
            'bases_datos': bases_datos
        })
    except UsuarioControlado.DoesNotExist:
        messages.error(request, "No se encontró su perfil de usuario controlado")
        return redirect('control:login')

@login_required
def crear_usuario(request):
    """Crear nuevo usuario con acceso controlado"""
    # Verificar que el usuario es admin
    try:
        admin_user = CustomUser.objects.get(username=request.user.username)
        if admin_user.tipo_usuario != 'ADMIN':
            raise PermissionDenied("No tiene permisos para crear usuarios")
    except CustomUser.DoesNotExist:
        raise PermissionDenied("Usuario no configurado correctamente")
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        nombres = request.POST['nombres']
        apellidos = request.POST['apellidos']
        documento = request.POST['documento']
        entidad = request.POST['entidad']
        cargo = request.POST['cargo']
        correo = request.POST['correo']
        tipo_usuario = request.POST['tipo_usuario']
        
        try:
            # Verificar que el usuario no existe
            if CustomUser.objects.filter(username=username).exists():
                raise ValueError("El nombre de usuario ya está en uso")
            
            # Validar tipo de usuario
            if tipo_usuario not in ['ADMIN', 'CONTROLADO']:
                raise ValueError("Tipo de usuario no válido")
            
            # Crear usuario
            user = CustomUser.objects.create(
                username=username,
                password=make_password(password),
                first_name=nombres,
                last_name=apellidos,
                email=correo,
                is_staff=tipo_usuario == 'ADMIN',
                tipo_usuario=tipo_usuario,
                is_active=True
            )
            
            # Crear usuario controlado si es tipo CONTROLADO
            if tipo_usuario == 'CONTROLADO':
                usuario_controlado = UsuarioControlado.objects.create(
                    usuario=user,
                    correo=correo,
                    nombres=nombres,
                    apellidos=apellidos,
                    documento=documento,
                    entidad=entidad,
                    cargo=cargo,
                    acuerdo_confidencialidad=request.FILES['acuerdo_confidencialidad']
                )
            
            messages.success(request, 'Usuario creado exitosamente')
            return redirect('control:ver_usuarios')
            
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Error al crear el usuario: {str(e)}")
            
    return render(request, 'control/crear_usuario.html')

@login_required
def subir_base_datos(request):
    """Subir nueva base de datos"""
    # Verificar que el usuario es admin
    try:
        custom_user = CustomUser.objects.get(username=request.user.username)
        if custom_user.tipo_usuario != 'ADMIN':
            raise PermissionDenied("No tiene permisos para subir bases de datos")
    except CustomUser.DoesNotExist:
        raise PermissionDenied("Usuario no configurado correctamente")
    
    if request.method == 'POST':
        nombre = request.POST['nombre']
        descripcion = request.POST['descripcion']
        archivo = request.FILES['archivo']
        
        try:
            # Validar que el archivo es CSV
            if not archivo.name.endswith('.csv'):
                raise ValueError("El archivo debe ser un archivo CSV")
            
            # Crear nueva base de datos
            base_datos = BaseDatos.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                archivo=archivo,
                subido_por=custom_user  # Asignar el usuario que sube el archivo
            )
            
            messages.success(request, 'Base de datos subida exitosamente')
            return redirect('control:dashboard_admin')
        except Exception as e:
            messages.error(request, f'Error al subir la base de datos: {str(e)}')
    
    return render(request, 'control/subir_base_datos.html')

@login_required
def asignar_permisos(request, base_id):
    """Asignar permisos de acceso a una base de datos"""
    # Verificar que el usuario es admin
    try:
        admin_user = CustomUser.objects.get(username=request.user.username)
        if admin_user.tipo_usuario != 'ADMIN':
            raise PermissionDenied("No tiene permisos para asignar permisos")
    except CustomUser.DoesNotExist:
        raise PermissionDenied("Usuario no configurado correctamente")
    
    base_datos = get_object_or_404(BaseDatos, id=base_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'asignar':
            usuario_id = request.POST.get('usuario')
            puede_descargar = request.POST.get('puede_descargar') == 'on'
            
            try:
                usuario_controlado = UsuarioControlado.objects.get(id=usuario_id)
                
                # Verificar si ya existe un permiso para este usuario y base de datos
                permiso_existente = PermisoBaseDatos.objects.filter(
                    usuario=usuario_controlado,
                    base_datos=base_datos
                ).first()
                
                if permiso_existente:
                    permiso_existente.puede_descargar = puede_descargar
                    permiso_existente.save()
                    messages.success(request, 'Permiso actualizado exitosamente')
                else:
                    PermisoBaseDatos.objects.create(
                        usuario=usuario_controlado,
                        base_datos=base_datos,
                        puede_descargar=puede_descargar
                    )
                    messages.success(request, 'Permiso asignado exitosamente')
                
                return redirect('control:ver_usuarios_base', base_id=base_id)
            except UsuarioControlado.DoesNotExist:
                messages.error(request, "Usuario no encontrado")
            except Exception as e:
                messages.error(request, f"Error al asignar permisos: {str(e)}")
        
        elif action == 'eliminar':
            permiso_id = request.POST.get('permiso_id')
            try:
                permiso = PermisoBaseDatos.objects.get(id=permiso_id)
                if permiso.base_datos.id == base_id:
                    permiso.delete()
                    messages.success(request, 'Permiso eliminado exitosamente')
                    return redirect('control:ver_usuarios_base', base_id=base_id)
                else:
                    messages.error(request, "El permiso no corresponde a esta base de datos")
            except PermisoBaseDatos.DoesNotExist:
                messages.error(request, "Permiso no encontrado")
            except Exception as e:
                messages.error(request, f"Error al eliminar permiso: {str(e)}")
    
    # Obtener usuarios controlados que no tienen permiso para esta base de datos
    usuarios_controlados = UsuarioControlado.objects.all()
    permisos = PermisoBaseDatos.objects.filter(base_datos=base_datos)
    
    return render(request, 'control/asignar_permisos.html', {
        'base_datos': base_datos,
        'usuarios_controlados': usuarios_controlados,
        'permisos': permisos
    })

@login_required
def ver_usuarios(request):
    """Ver lista de usuarios"""
    # Verificar que el usuario es admin
    try:
        admin_user = CustomUser.objects.get(username=request.user.username)
        if admin_user.tipo_usuario != 'ADMIN':
            raise PermissionDenied("No tiene permisos para ver usuarios")
    except CustomUser.DoesNotExist:
        raise PermissionDenied("Usuario no configurado correctamente")
    
    usuarios = CustomUser.objects.all()
    return render(request, 'control/ver_usuarios.html', {
        'usuarios': usuarios
    })

@login_required
def ver_bases_datos(request):
    """Ver lista de bases de datos"""
    # Verificar que el usuario es admin
    try:
        admin_user = CustomUser.objects.get(username=request.user.username)
        if admin_user.tipo_usuario != 'ADMIN':
            raise PermissionDenied("No tiene permisos para ver bases de datos")
    except CustomUser.DoesNotExist:
        raise PermissionDenied("Usuario no configurado correctamente")
    
    bases_datos = BaseDatos.objects.all()
    return render(request, 'control/ver_bases_datos.html', {
        'bases_datos': bases_datos
    })

@login_required
def ver_permisos(request):
    """Ver lista de permisos"""
    # Verificar que el usuario es admin
    try:
        admin_user = CustomUser.objects.get(username=request.user.username)
        if admin_user.tipo_usuario != 'ADMIN':
            raise PermissionDenied("No tiene permisos para ver permisos")
    except CustomUser.DoesNotExist:
        raise PermissionDenied("Usuario no configurado correctamente")
    
    permisos = PermisoBaseDatos.objects.all()
    return render(request, 'control/ver_permisos.html', {
        'permisos': permisos
    })

@login_required
def ver_permisos_usuario(request, usuario_id):
    """Ver permisos de un usuario específico"""
    # Verificar que el usuario es admin
    try:
        admin_user = CustomUser.objects.get(username=request.user.username)
        if admin_user.tipo_usuario != 'ADMIN':
            raise PermissionDenied("No tiene permisos para ver permisos")
    except CustomUser.DoesNotExist:
        raise PermissionDenied("Usuario no configurado correctamente")
    
    try:
        usuario = CustomUser.objects.get(id=usuario_id)
        usuario_controlado = None
        
        # Obtener el usuario controlado si existe
        if usuario.tipo_usuario == 'CONTROLADO':
            try:
                usuario_controlado = UsuarioControlado.objects.get(usuario=usuario)
            except UsuarioControlado.DoesNotExist:
                usuario_controlado = None
        
        # Obtener los permisos usando el usuario controlado si existe
        if usuario_controlado:
            permisos = PermisoBaseDatos.objects.filter(usuario=usuario_controlado)
        else:
            permisos = []
        
        return render(request, 'control/ver_permisos_usuario.html', {
            'usuario': usuario,
            'usuario_controlado': usuario_controlado,
            'permisos': permisos
        })
    except CustomUser.DoesNotExist:
        messages.error(request, "Usuario no encontrado")
        return redirect('control:dashboard_admin')

@login_required
def ver_base_datos(request, base_id):
    """Ver contenido de una base de datos"""
    base_datos = get_object_or_404(BaseDatos, id=base_id)
    
    # Verificar permisos para usuarios controlados
    if not request.user.is_staff:
        try:
            custom_user = CustomUser.objects.get(username=request.user.username)
            if custom_user.tipo_usuario == 'CONTROLADO':
                usuario_controlado = UsuarioControlado.objects.get(usuario=custom_user)
                permiso = PermisoBaseDatos.objects.filter(
                    usuario=usuario_controlado, 
                    base_datos=base_datos
                ).first()
                if not permiso:
                    raise PermissionDenied("No tiene permisos para ver esta base de datos")
                
                # Verificar si tiene permiso para descargar
                puede_descargar = permiso.puede_descargar
            else:
                raise PermissionDenied("Tipo de usuario no válido")
        except CustomUser.DoesNotExist:
            raise PermissionDenied("Usuario no configurado correctamente")
        except UsuarioControlado.DoesNotExist:
            raise PermissionDenied("Usuario no configurado correctamente")
    else:
        puede_descargar = True  # Los administradores siempre pueden descargar
    
    try:
        # Leer el CSV con encoding UTF-8 y manejo de errores
        df = pd.read_csv(base_datos.archivo.path, encoding='utf-8', encoding_errors='replace')
        
        # Convertir el DataFrame a un formato que pueda ser serializado
        data = df.to_dict('records')
        
        # Limpiar los datos para evitar problemas con caracteres especiales
        for fila in data:
            for key, value in fila.items():
                if isinstance(value, str):
                    # Reemplazar caracteres problemáticos
                    fila[key] = value.replace('|', '¦').replace('[', '⟦').replace(']', '⟧')
        
        return render(request, 'control/ver_base_datos.html', {
            'base_datos': base_datos,
            'data': data,
            'columnas': df.columns.tolist(),
            'puede_descargar': puede_descargar
        })
    except Exception as e:
        messages.error(request, f'Error al procesar la base de datos: {str(e)}')
        return redirect('control:dashboard_usuario')

@login_required
def descargar_base_datos(request, base_id):
    """Descargar una base de datos"""
    base_datos = get_object_or_404(BaseDatos, id=base_id)
    
    # Verificar permisos
    if not request.user.is_staff:
        usuario_controlado = get_object_or_404(UsuarioControlado, usuario=CustomUser.objects.get(username=request.user.username))
        permiso = PermisoBaseDatos.objects.filter(
            usuario=usuario_controlado,
            base_datos=base_datos,
            puede_descargar=True
        ).exists()
        if not permiso:
            raise PermissionDenied("No tiene permisos para descargar esta base de datos")
    
    try:
        # Registrar acceso
        LogAcceso.objects.create(
            usuario=CustomUser.objects.get(username=request.user.username),
            base_datos=base_datos,
            accion='DESCARGAR'
        )
        
        # Leer el archivo CSV
        df = pd.read_csv(base_datos.archivo.path)
        
        # Crear respuesta con el archivo
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{base_datos.nombre}.csv"'
        df.to_csv(response, index=False)
        
        return response
    except Exception as e:
        messages.error(request, f'Error al procesar la base de datos: {str(e)}')
        return redirect('control:dashboard_usuario')

@login_required
def editar_usuario(request, usuario_id):
    """Editar datos de un usuario existente"""
    # Verificar que el usuario es admin
    try:
        admin_user = CustomUser.objects.get(username=request.user.username)
        if admin_user.tipo_usuario != 'ADMIN':
            raise PermissionDenied("No tiene permisos para editar usuarios")
    except CustomUser.DoesNotExist:
        raise PermissionDenied("Usuario no configurado correctamente")
    
    try:
        usuario = CustomUser.objects.get(id=usuario_id)
        usuario_controlado = None
        if usuario.tipo_usuario == 'CONTROLADO':
            usuario_controlado = UsuarioControlado.objects.get(usuario=usuario)
    except CustomUser.DoesNotExist:
        raise Http404("Usuario no encontrado")
    except UsuarioControlado.DoesNotExist:
        usuario_controlado = None
    
    if request.method == 'POST':
        username = request.POST['username']
        nombres = request.POST['nombres']
        apellidos = request.POST['apellidos']
        correo = request.POST['correo']
        documento = request.POST['documento']
        entidad = request.POST['entidad']
        cargo = request.POST['cargo']
        tipo_usuario = request.POST['tipo_usuario']
        nueva_contraseña = request.POST.get('nueva_contraseña')
        
        try:
            # Verificar que el username no está en uso por otro usuario
            if CustomUser.objects.filter(username=username).exclude(id=usuario_id).exists():
                raise ValueError("El nombre de usuario ya está en uso")
            
            # Validar tipo de usuario
            if tipo_usuario not in ['ADMIN', 'CONTROLADO']:
                raise ValueError("Tipo de usuario no válido")
            
            # Actualizar datos del usuario
            usuario.username = username
            usuario.first_name = nombres
            usuario.last_name = apellidos
            usuario.email = correo
            usuario.tipo_usuario = tipo_usuario
            usuario.is_staff = tipo_usuario == 'ADMIN'
            usuario.is_active = True  # Asegurar que el usuario esté activo
            
            # Actualizar la contraseña si se proporciona una nueva
            if nueva_contraseña:
                usuario.password = make_password(nueva_contraseña)
            
            usuario.save()
            
            # Actualizar datos del usuario controlado si existe
            if usuario_controlado:
                usuario_controlado.correo = correo
                usuario_controlado.nombres = nombres
                usuario_controlado.apellidos = apellidos
                usuario_controlado.documento = documento
                usuario_controlado.entidad = entidad
                usuario_controlado.cargo = cargo
                
                # Actualizar acuerdo de confidencialidad si se sube uno nuevo
                if 'acuerdo_confidencialidad' in request.FILES:
                    usuario_controlado.acuerdo_confidencialidad = request.FILES['acuerdo_confidencialidad']
                
                usuario_controlado.save()
            
            messages.success(request, 'Usuario actualizado exitosamente')
            return redirect('control:dashboard_admin')
            
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al actualizar el usuario: {str(e)}')
    
    return render(request, 'control/editar_usuario.html', {
        'usuario': usuario,
        'usuario_controlado': usuario_controlado
    })

@login_required
def editar_permiso(request, permiso_id):
    """Editar permisos de acceso a una base de datos"""
    # Verificar que el usuario es admin
    try:
        admin_user = CustomUser.objects.get(username=request.user.username)
        if admin_user.tipo_usuario != 'ADMIN':
            raise PermissionDenied("No tiene permisos para editar permisos")
    except CustomUser.DoesNotExist:
        raise PermissionDenied("Usuario no configurado correctamente")
    
    try:
        permiso = PermisoBaseDatos.objects.get(id=permiso_id)
    except PermisoBaseDatos.DoesNotExist:
        raise Http404("Permiso no encontrado")
    
    if request.method == 'POST':
        puede_descargar = request.POST.get('puede_descargar') == 'on'
        
        permiso.puede_descargar = puede_descargar
        permiso.save()
        
        messages.success(request, 'Permiso actualizado exitosamente')
        return redirect('control:ver_permisos')
    
    return render(request, 'control/editar_permiso.html', {
        'permiso': permiso
    })

@login_required
def ver_usuarios_base(request, base_id):
    """Ver usuarios con acceso a una base de datos"""
    # Verificar que el usuario es admin
    try:
        admin_user = CustomUser.objects.get(username=request.user.username)
        if admin_user.tipo_usuario != 'ADMIN':
            raise PermissionDenied("No tiene permisos para ver los usuarios")
    except CustomUser.DoesNotExist:
        raise PermissionDenied("Usuario no configurado correctamente")
    
    base_datos = get_object_or_404(BaseDatos, id=base_id)
    permisos = PermisoBaseDatos.objects.filter(base_datos=base_datos)
    
    return render(request, 'control/ver_usuarios_base.html', {
        'base_datos': base_datos,
        'permisos': permisos
    })

def login_view(request):
    """Vista de inicio de sesión"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Intentar autenticar
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            try:
                custom_user = CustomUser.objects.get(username=username)
                
                # Verificar que el usuario está activo
                if not user.is_active:
                    raise PermissionDenied("La cuenta está desactivada")
                    
                # Verificar que el tipo de usuario es válido
                if custom_user.tipo_usuario not in ['ADMIN', 'CONTROLADO']:
                    raise PermissionDenied("Tipo de usuario no válido")
                    
                login(request, user)
                
                # Actualizar el contexto para incluir el tipo de usuario
                request.session['tipo_usuario'] = custom_user.tipo_usuario
                
                # Redirigir según el tipo de usuario
                if custom_user.tipo_usuario == 'ADMIN':
                    return redirect('control:dashboard_admin')
                elif custom_user.tipo_usuario == 'CONTROLADO':
                    return redirect('control:dashboard_usuario')
                else:
                    raise PermissionDenied("Tipo de usuario no válido")
                    
            except CustomUser.DoesNotExist:
                messages.error(request, "Usuario no encontrado")
            except PermissionDenied as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Credenciales inválidas')
    
    return render(request, 'control/login.html')

def logout_view(request):
    """Vista de logout"""
    logout(request)
    return redirect('control:login')
