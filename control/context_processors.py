from django.contrib.auth.models import User
from control.models import CustomUser

def tipo_usuario(request):
    """Procesador de contexto para el tipo de usuario"""
    if request.user.is_authenticated:
        try:
            custom_user = CustomUser.objects.get(username=request.user.username)
            return {'tipo_usuario': custom_user.tipo_usuario}
        except CustomUser.DoesNotExist:
            return {'tipo_usuario': None}
    return {'tipo_usuario': None}
