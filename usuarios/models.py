from django.db.models import CASCADE
import uuid
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from IdenticSenaPy import settings

class Usuario(AbstractUser):

    ROL_CHOICES = [
        ('admin',     'Administrador'),
        ('vigilante', 'Vigilante'),
        ('aprendiz', 'Aprendiz'),
        ('instructor','Instructor'),
    ]

    email           = models.EmailField(unique=True)
    tipoDocumento   = models.CharField(max_length=2)
    numeroDocumento = models.CharField(max_length=20, unique=True)
    nombre          = models.CharField(max_length=50)
    apellido        = models.CharField(max_length=50)
    edad            = models.PositiveIntegerField(blank=True, null=True)
    telefono        = models.CharField(max_length=15, blank=True, null=True)

    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='aprendiz',
    )

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username', 'nombre', 'apellido']

    def __str__(self):
        return f"{self.email} - {self.nombre} {self.apellido}"

class PermisoRol(models.Model):
    """Define qué secciones puede acceder cada rol."""

    SECCIONES = [
        ('dashboard_admin',    'Panel de administración'),
        ('dashboard_vigilante','Panel de vigilante'),
        ('dashboard_estudiante','Panel de estudiante'),
        ('ver_usuarios',       'Ver lista de usuarios'),
        ('editar_roles',       'Editar roles de usuarios'),
        ('gestionar_permisos', 'Gestionar permisos'),
        ('registrar_entrada',  'Registrar entrada/salida'),
        ('ver_qr',             'Ver código QR propio'),
        ('vincular_dispositivos', 'Vincular dispositivos'),
    ]

    rol      = models.CharField(max_length=20, choices=Usuario.ROL_CHOICES, unique=True)
    permisos = models.JSONField(default=list)  # lista de claves de SECCIONES

    class Meta:
        verbose_name        = 'Permiso de rol'
        verbose_name_plural = 'Permisos de roles'

    def __str__(self):
        return f"Permisos — {self.get_rol_display()}"

    def get_rol_display(self):
        return dict(Usuario.ROL_CHOICES).get(self.rol, self.rol)

    def tiene_permiso(self, seccion):
        return seccion in self.permisos

class Equipo(models.Model):
    estudiante = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='equipos'
    )
    nombre = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    serial = models.CharField(max_length=100, unique=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.marca} ({self.serial}) - {self.estudiante.email}"

class Ficha(models.Model):

    codigo = models.CharField(
        max_length=20,
        unique=True
    )

    programa = models.CharField(
        max_length=200
    )

    jornada = models.CharField(
        max_length=50
    )


    aprendices = models.ManyToManyField(
        Usuario,
        limit_choices_to={'rol': 'aprendiz'},
        related_name="fichas"
    )


    def __str__(self):
        return f"{self.codigo} - {self.programa}"

class Aula(models.Model):
    nombre = models.CharField(max_length=100)
    bloque = models.CharField(max_length=100)
    capacidad = models.PositiveIntegerField()

    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="aulas"
    )

    def __str__(self):
        return self.nombre

class InstructorFicha(models.Model):

    instructor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'instructor'}
    )

    ficha = models.ForeignKey(
        Ficha,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('instructor', 'ficha')

class FichaAula(models.Model):

    ficha = models.ForeignKey(
        Ficha,
        on_delete=models.CASCADE
    )

    aula = models.ForeignKey(
        Aula,
        on_delete=models.CASCADE
    )

    jornada = models.CharField(
        max_length=20,
        default="Mañana"
    )

    class Meta:
        unique_together = ('ficha', 'aula')

class RegistroAsistencia(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='asistencias')
    hora_entrada = models.DateTimeField(auto_now_add=True)
    hora_salida = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.hora_entrada.strftime('%Y-%m-%d %H:%M')}"

class TokenQR(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='tokens_qr')
    creado_en = models.DateTimeField(auto_now_add=True)
    expira_en = models.DateTimeField()
    usado = models.BooleanField(default=False)

    def es_valido(self):
        return not self.usado and timezone.now() <= self.expira_en

    def __str__(self):
        return f"QR {self.usuario.nombre} - {'Usado' if self.usado else 'Activo'}"