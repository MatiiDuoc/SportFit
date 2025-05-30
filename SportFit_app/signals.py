from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .models import Usuario
from django.db.models.signals import post_save
from django.contrib.auth.models import User


@receiver(user_signed_up)
def create_usuario_social(sender, request, user, **kwargs):
    if not Usuario.objects.filter(correo=user.email).exists():
        Usuario.objects.create(
            nombre=user.first_name or '',
            apellido=user.last_name or '',
            correo=user.email,
            rut='',
            telefono='',
            tel_emergencia='',
            contrasena=user.password,
            direccion='',
            id_comuna_id=3,   # Usa un ID válido existente en tu tabla comuna
            id_genero_id=1,   # Usa un ID válido existente en tu tabla genero
            tipo_usuario='cliente',
        )

@receiver(post_save, sender=User)
def create_usuario_for_superuser(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        if not Usuario.objects.filter(correo=instance.email).exists():
            Usuario.objects.create(
                rut='00000000-0',
                nombre=instance.first_name or 'Admin',
                apellido=instance.last_name or '',
                correo=instance.email,
                telefono='999999999',
                tel_emergencia='999999999',
                contrasena=instance.password,
                direccion='Sin dirección',
                id_comuna_id=13,   # Usa un ID válido existente en tu tabla comuna
                id_genero_id=1,   # Usa un ID válido existente en tu tabla genero
                tipo_usuario='administrador',
                id_entrenador=None,
                id_plan=None,
            )