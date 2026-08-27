from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import RegistroAsistencia, TokenQR
from django.views.decorators.http import require_POST
from .forms import RegistroForm, LoginForm
import csv
from django.http import HttpResponse
from .models import RegistroAsistencia 
from .models import (
    Usuario,
    Equipo,
    PermisoRol,
    Ficha,
    Aula,
    InstructorFicha,
    FichaAula
)


# ==========================
# ROLES
# ==========================

def es_admin(user):
    return user.is_authenticated and (
        user.is_staff or user.rol == 'admin'
    )


def es_vigilante(user):
    return user.is_authenticated and user.rol == 'vigilante'


def es_instructor(user):
    return user.is_authenticated and user.rol == 'instructor'

def es_aprendiz(user):
    return user.is_authenticated and user.rol == 'aprendiz'


# ==========================
# AUTENTICACIÓN
# ==========================

def registro(request):

    if request.method == 'POST':

        form = RegistroForm(request.POST)

        if form.is_valid():

            usuario = form.save()

            auth_login(
                request,
                usuario
            )

            return redirect('perfil')

    else:

        form = RegistroForm()


    return render(
        request,
        'usuarios/registro.html',
        {
            'form': form
        }
    )



def login(request):

    if request.method == 'POST':

        form = LoginForm(
            request,
            data=request.POST
        )


        if form.is_valid():

            usuario = form.get_user()

            auth_login(
                request,
                usuario
            )


            if usuario.is_staff or usuario.rol == 'admin':

                return redirect(
                    'dashboard'
                )


            if usuario.rol == 'vigilante':

                return redirect(
                    'panel_vigilante'
                )


            if usuario.rol == 'instructor':

                return redirect(
                    'dashboard_instructor'
                )


            return redirect(
                'inicio'
            )


        messages.error(
            request,
            'Correo electrónico o contraseña incorrectos.'
        )


    else:

        form = LoginForm()



    return render(
        request,
        'usuarios/login.html',
        {
            'form': form
        }
    )



def logout(request):

    auth_logout(
        request
    )

    return redirect(
        'login'
    )



@login_required
def perfil(request):

    signer = TimestampSigner()


    documento = getattr(
        request.user,
        'numeroDocumento',
        str(request.user.id)
    )


    token_qr = signer.sign(
        str(documento)
    )


    return render(
        request,
        'usuarios/perfil.html',
        {
            'token_qr': token_qr
        }
    )

@login_required
def inicio_view(request):
    signer = TimestampSigner()

    documento = getattr(
        request.user,
        'numeroDocumento',
        str(request.user.id)
    )

    token_qr = signer.sign(
        str(documento)
    )

    return render(
        request,
        'usuarios/inicio.html',
        {
            'token_qr': token_qr
        }
    )


# ==========================
# DASHBOARD ADMIN
# ==========================

@login_required
@user_passes_test(es_admin, login_url='login')
def dashboard(request):

    total = Usuario.objects.count()


    activos = Usuario.objects.filter(
        is_active=True
    ).count()


    vigilantes = Usuario.objects.filter(
        rol='vigilante'
    ).count()


    aprendices = Usuario.objects.filter(
        rol='aprendiz'
    ).count()


    instructores = Usuario.objects.filter(
        rol='instructor'
    ).count()


    recientes = Usuario.objects.order_by(
        '-date_joined'
    )[:6]


    return render(
        request,
        'usuarios/dashboard.html',
        {
            'total': total,
            'activos': activos,
            'vigilantes': vigilantes,
            'aprendices': aprendices,
            'instructores': instructores,
            'recientes': recientes
        }
    )



# ==========================
# USUARIOS
# ==========================

@login_required
@user_passes_test(es_admin, login_url='login')
def dashboard_usuarios(request):

    query = request.GET.get(
        'q',
        ''
    )

    rol = request.GET.get(
        'rol',
        ''
    )


    usuarios = Usuario.objects.all().order_by(
        '-date_joined'
    )


    if query:

        usuarios = usuarios.filter(
            nombre__icontains=query
        ) | usuarios.filter(
            apellido__icontains=query
        ) | usuarios.filter(
            email__icontains=query
        )


    if rol:

        usuarios = usuarios.filter(
            rol=rol
        )


    return render(
        request,
        'usuarios/dashboard_usuarios.html',
        {
            'usuarios': usuarios,
            'query': query,
            'rol_filtro': rol,
            'roles': Usuario.ROL_CHOICES,
            'fichas':Ficha.objects.all(),
        }
    )



@login_required
@user_passes_test(es_admin, login_url='login')
def crear_usuario(request):

    if request.method == 'POST':

        usuario = Usuario.objects.create_user(

        username=request.POST.get('email'),

        email=request.POST.get('email'),

        password=request.POST.get('password'),

        nombre=request.POST.get('nombre'),

        apellido=request.POST.get('apellido'),

        tipoDocumento=request.POST.get('tipoDocumento'),

        numeroDocumento=request.POST.get('numeroDocumento'),

        rol=request.POST.get('rol')
    )


    ficha_id = request.POST.get('ficha')

    if ficha_id:
        usuario.fichas.add(ficha_id)


        messages.success(
            request,
            'Usuario creado correctamente.'
        )


    return redirect(
        'dashboard_usuarios'
    )

@login_required
@user_passes_test(es_admin, login_url='login')
def editar_usuario(request, user_id):

    usuario = get_object_or_404(
        Usuario,
        id=user_id
    )


    if request.method == 'POST':

        usuario.nombre = request.POST.get('nombre')
        usuario.apellido = request.POST.get('apellido')
        usuario.email = request.POST.get('email')
        usuario.tipoDocumento = request.POST.get('tipoDocumento')
        usuario.numeroDocumento = request.POST.get('numeroDocumento')
        usuario.rol = request.POST.get('rol')

        usuario.save()

        ficha_id = request.POST.get('ficha')

        usuario.fichas.clear()

        if ficha_id:
            usuario.fichas.add(ficha_id)


        messages.success(
            request,
            'Usuario actualizado correctamente.'
        )


    return redirect(
        'dashboard_usuarios'
    )



@login_required
@user_passes_test(es_admin, login_url='login')
def eliminar_usuario(request, user_id):

    usuario = get_object_or_404(
        Usuario,
        id=user_id
    )


    if request.method == 'POST':

        usuario.delete()

        messages.success(
            request,
            'Usuario eliminado correctamente.'
        )


    return redirect(
        'dashboard_usuarios'
    )



@login_required
@user_passes_test(es_admin, login_url='login')
def dashboard_toggle(request, user_id):

    usuario = get_object_or_404(
        Usuario,
        id=user_id
    )


    if request.method == 'POST':

        if usuario == request.user:

            messages.error(
                request,
                'No puedes desactivar tu propia cuenta.'
            )

        else:

            usuario.is_active = not usuario.is_active
            usuario.save()


            estado = (
                'activado'
                if usuario.is_active
                else 'desactivado'
            )


            messages.success(
                request,
                f'Usuario {estado} correctamente.'
            )


    return redirect(
        'dashboard_usuarios'
    )



@login_required
@user_passes_test(es_admin, login_url='login')
def dashboard_editar_rol(request, user_id):

    usuario = get_object_or_404(
        Usuario,
        id=user_id
    )


    if request.method == 'POST':

        nuevo_rol = request.POST.get(
            'rol'
        )


        roles_validos = [
            r[0]
            for r in Usuario.ROL_CHOICES
        ]


        if nuevo_rol not in roles_validos:

            messages.error(
                request,
                'Rol inválido.'
            )

            return redirect(
                'dashboard_usuarios'
            )


        usuario.rol = nuevo_rol

        usuario.is_staff = (
            nuevo_rol == 'admin'
        )

        usuario.save()


        messages.success(
            request,
            'Rol actualizado correctamente.'
        )


    return redirect(
        'dashboard_usuarios'
    )



# ==========================
# PERMISOS
# ==========================

@login_required
@user_passes_test(es_admin, login_url='login')
def dashboard_permisos(request):

    for rol, _ in Usuario.ROL_CHOICES:

        PermisoRol.objects.get_or_create(
            rol=rol
        )


    permisos = PermisoRol.objects.all()


    return render(
        request,
        'usuarios/dashboard_permisos.html',
        {
            'permisos_roles': permisos,
            'secciones': PermisoRol.SECCIONES
        }
    )



@login_required
@user_passes_test(es_admin, login_url='login')
def dashboard_permisos_guardar(request, rol):

    if request.method == 'POST':

        permisos_validos = [
            p[0]
            for p in PermisoRol.SECCIONES
        ]


        seleccionados = [
            p
            for p in request.POST.getlist('permisos')
            if p in permisos_validos
        ]


        permiso, _ = PermisoRol.objects.get_or_create(
            rol=rol
        )


        permiso.permisos = seleccionados

        permiso.save()


        messages.success(
            request,
            'Permisos actualizados correctamente.'
        )


    return redirect(
        'dashboard_permisos'
    )



# ==========================
# EQUIPOS
# ==========================

@login_required
def gestionar_equipos(request):

    equipos = Equipo.objects.filter(
        estudiante=request.user
    )


    if request.method == 'POST':

        nombre = request.POST.get('nombre')
        marca = request.POST.get('marca')
        serial = request.POST.get('serial')


        if equipos.count() >= 3:

            messages.error(
                request,
                'Solo se permiten registrar máximo 3 equipos.'
            )

            return redirect(
                'gestionar_equipos'
            )


        if Equipo.objects.filter(
            serial=serial
        ).exists():

            messages.error(
                request,
                'Ya existe un equipo con ese serial.'
            )

            return redirect(
                'gestionar_equipos'
            )


        Equipo.objects.create(
            estudiante=request.user,
            nombre=nombre,
            marca=marca,
            serial=serial
        )


        messages.success(
            request,
            'Equipo registrado correctamente.'
        )


        return redirect(
            'gestionar_equipos'
        )


    return render(
        request,
        'usuarios/gestionar_equipos.html',
        {
            'equipos': equipos
        }
    )



@login_required
def eliminar_equipo(request, equipo_id):

    equipo = get_object_or_404(
        Equipo,
        id=equipo_id,
        estudiante=request.user
    )


    equipo.delete()


    messages.success(
        request,
        'Equipo eliminado correctamente.'
    )


    return redirect(
        'gestionar_equipos'
    )

# ==========================
# VIGILANTE / QR
# ==========================

@login_required
def panel_vigilante(request):

    return render(
        request,
        'usuarios/panel_vigilante.html'
    )



@login_required
def verificar_aprendiz_simple(request, token):
    try:
        # 1. Buscar el token en la base de datos
        token_qr = TokenQR.objects.select_related('usuario').get(id=token)

        # 2. Validar si ya fue usado
        if token_qr.usado:
            return JsonResponse({
                'encontrado': False, 
                'mensaje': 'Este código QR ya ha sido utilizado anteriormente.'
            }, status=400)

        # 3. Validar si ya expiró por tiempo
        if timezone.now() > token_qr.expira_en:
            return JsonResponse({
                'encontrado': False, 
                'mensaje': 'El código QR ha expirado. Por favor, genere uno nuevo.'
            }, status=400)

        # 4. MARCAR EL TOKEN COMO USADO INMEDIATAMENTE (Aquí "muere" el QR)
        token_qr.usado = True
        token_qr.save()

        aprendiz = token_qr.usuario
        hoy = timezone.now().date()

        # 5. Registrar asistencia (Entrada o Salida)
        registro_activo = RegistroAsistencia.objects.filter(
            usuario=aprendiz,
            hora_entrada__date=hoy,
            hora_salida__isnull=True
        ).first()

        if registro_activo:
            registro_activo.hora_salida = timezone.now()
            registro_activo.save()
            tipo_movimiento = 'SALIDA'
        else:
            RegistroAsistencia.objects.create(
                usuario=aprendiz,
                hora_entrada=timezone.now()
            )
            tipo_movimiento = 'ENTRADA'

        equipos = [
            {
                'nombre': equipo.nombre,
                'marca': equipo.marca,
                'serial': equipo.serial
            }
            for equipo in aprendiz.equipos.all()
        ]

        return JsonResponse({
            'encontrado': True,
            'estado': 'ACTIVO',
            'movimiento': tipo_movimiento,
            'tipo_documento': aprendiz.tipoDocumento,
            'numero_documento': aprendiz.numeroDocumento,
            'nombre': aprendiz.nombre,
            'apellido': aprendiz.apellido,
            'email': aprendiz.email,
            'telefono': aprendiz.telefono,
            'equipos': equipos
        })

    except TokenQR.DoesNotExist:
        return JsonResponse({
            'encontrado': False, 
            'mensaje': 'Código QR inválido o inexistente.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'encontrado': False, 
            'mensaje': f'Error al procesar el código: {str(e)}'
        }, status=500)



# ==========================
# FICHAS
# ==========================

@login_required
@user_passes_test(es_admin, login_url='login')
def dashboard_fichas(request):

    query = request.GET.get(
        'q',
        ''
    )


    fichas = Ficha.objects.all().order_by(
        'codigo'
    )


    if query:

        fichas = fichas.filter(
            codigo__icontains=query
        ) | fichas.filter(
            programa__icontains=query
        )


    return render(
        request,
        'usuarios/dashboard_fichas.html',
        {
            'fichas': fichas,
            'query': query
        }
    )



@login_required
@user_passes_test(es_admin, login_url='login')
def crear_ficha(request):

    if request.method == 'POST':

        codigo = request.POST.get('codigo')
        programa = request.POST.get('programa')
        jornada = request.POST.get('jornada')


        Ficha.objects.create(
            codigo=codigo,
            programa=programa,
            jornada=jornada
        )


        messages.success(
            request,
            'Ficha creada correctamente.'
        )


    return redirect(
        'dashboard_fichas'
    )



@login_required
@user_passes_test(es_admin, login_url='login')
def editar_ficha(request, ficha_id):

    ficha = get_object_or_404(
        Ficha,
        id=ficha_id
    )


    if request.method == 'POST':

        ficha.codigo = request.POST.get('codigo')
        ficha.programa = request.POST.get('programa')
        ficha.jornada = request.POST.get('jornada')

        ficha.save()


        messages.success(
            request,
            'Ficha actualizada correctamente.'
        )


    return redirect(
        'dashboard_fichas'
    )



@login_required
@user_passes_test(es_admin, login_url='login')
def eliminar_ficha(request, ficha_id):

    ficha = get_object_or_404(
        Ficha,
        id=ficha_id
    )


    if request.method == 'POST':

        ficha.delete()


        messages.success(
            request,
            'Ficha eliminada correctamente.'
        )


    return redirect(
        'dashboard_fichas'
    )



# ==========================
# AULAS
# ==========================

@login_required
@user_passes_test(es_instructor, login_url='login')
def dashboard_aulas(request):

    aulas = Aula.objects.filter(
        creado_por=request.user
    ).order_by(
        'nombre'
    )


    return render(
        request,
        'usuarios/dashboard_aulas.html',
        {
            'aulas': aulas
        }
    )



@login_required
@user_passes_test(es_instructor, login_url='login')
def crear_aula(request):

    if request.method == 'POST':

        Aula.objects.create(
            nombre=request.POST.get('nombre'),
            bloque=request.POST.get('bloque'),
            capacidad=request.POST.get('capacidad'),
            creado_por=request.user
        )


        messages.success(
            request,
            'Aula creada correctamente.'
        )


    return redirect(
        'dashboard_aulas'
    )



@login_required
@user_passes_test(es_instructor, login_url='login')
def editar_aula(request, aula_id):

    aula = get_object_or_404(
        Aula,
        id=aula_id,
        creado_por=request.user
    )


    if request.method == 'POST':

        aula.nombre = request.POST.get('nombre')
        aula.bloque = request.POST.get('bloque')
        aula.capacidad = request.POST.get('capacidad')

        aula.save()


        messages.success(
            request,
            'Aula actualizada correctamente.'
        )


    return redirect(
        'dashboard_aulas'
    )



@login_required
@user_passes_test(es_instructor, login_url='login')
def eliminar_aula(request, aula_id):

    aula = get_object_or_404(
        Aula,
        id=aula_id,
        creado_por=request.user
    )


    if request.method == 'POST':

        aula.delete()


        messages.success(
            request,
            'Aula eliminada correctamente.'
        )


    return redirect(
        'dashboard_aulas'
    )



# ==========================
# ASIGNAR FICHAS A INSTRUCTOR
# ==========================

@login_required
@user_passes_test(es_admin, login_url='login')
def dashboard_asignar_fichas(request):

    instructores = Usuario.objects.filter(
        rol='instructor'
    )


    fichas = Ficha.objects.all()


    asignaciones = InstructorFicha.objects.select_related(
        'instructor',
        'ficha'
    )


    return render(
        request,
        'usuarios/dashboard_asignar_fichas.html',
        {
            'instructores': instructores,
            'fichas': fichas,
            'asignaciones': asignaciones
        }
    )



@login_required
@user_passes_test(es_admin, login_url='login')
def crear_asignacion_ficha(request):

    if request.method == 'POST':

        instructor = get_object_or_404(
            Usuario,
            id=request.POST.get('instructor'),
            rol='instructor'
        )


        ficha = get_object_or_404(
            Ficha,
            id=request.POST.get('ficha')
        )


        InstructorFicha.objects.get_or_create(
            instructor=instructor,
            ficha=ficha
        )


        messages.success(
            request,
            'Ficha asignada correctamente.'
        )


    return redirect(
        'dashboard_asignar_fichas'
    )



@login_required
@user_passes_test(es_admin, login_url='login')
def eliminar_asignacion_ficha(request, asignacion_id):

    asignacion = get_object_or_404(
        InstructorFicha,
        id=asignacion_id
    )


    if request.method == 'POST':

        asignacion.delete()


        messages.success(
            request,
            'Asignación eliminada correctamente.'
        )


    return redirect(
        'dashboard_asignar_fichas'
    )



# ==========================
# FICHA - AULA
# ==========================

@login_required
@user_passes_test(es_admin, login_url='login')
def dashboard_ficha_aula(request):

    contexto = {

        "fichas_aulas": FichaAula.objects.select_related(
            "ficha",
            "aula"
        ),

        "fichas": Ficha.objects.all(),

        "aulas": Aula.objects.all()

    }


    return render(
    request,
    "usuarios/dashboard_ficha_aula.html",
    contexto
)



@login_required
@user_passes_test(es_admin, login_url='login')
def crear_ficha_aula(request):

    if request.method == 'POST':

        FichaAula.objects.create(
            ficha_id=request.POST.get('ficha'),
            aula_id=request.POST.get('aula')
        )


        messages.success(
            request,
            'Ficha asignada al aula correctamente.'
        )


    return redirect(
        'dashboard_ficha_aula'
    )



@login_required
@user_passes_test(es_admin, login_url='login')
def editar_ficha_aula(request, relacion_id):

    relacion = get_object_or_404(
        FichaAula,
        id=relacion_id
    )


    if request.method == 'POST':

        relacion.ficha_id = request.POST.get('ficha')
        relacion.aula_id = request.POST.get('aula')

        relacion.save()


    return redirect(
        'dashboard_ficha_aula'
    )



@login_required
@user_passes_test(es_admin, login_url='login')
def eliminar_ficha_aula(request, relacion_id):

    relacion = get_object_or_404(
        FichaAula,
        id=relacion_id
    )


    if request.method == 'POST':

        relacion.delete()


    return redirect(
        'dashboard_ficha_aula'
    )



# ==========================
# INSTRUCTOR
# ==========================

@login_required
@user_passes_test(es_instructor, login_url='login')
def dashboard_instructor(request):

    usuario = request.user

    fichas = InstructorFicha.objects.filter(
        instructor=usuario
    ).select_related(
        "ficha"
    )

    fichas_instructor = fichas.values_list(
        'ficha_id',
        flat=True
    )

    relaciones = FichaAula.objects.filter(
        ficha_id__in=fichas_instructor
    ).select_related(
        'ficha',
        'aula'
    )

    aulas = Aula.objects.filter(
        id__in=relaciones.values_list(
            'aula_id',
            flat=True
        )
    ).distinct()

    contexto = {

        "fichas": fichas,

        "aulas": aulas,

        "fichas_aulas": relaciones

    }

    return render(
        request,
        "usuarios/dashboard_instructor.html",
        contexto
    )



@login_required
@user_passes_test(es_instructor, login_url='login')
def panel_instructor(request):

    return dashboard_instructor(
        request
    )


@login_required
@user_passes_test(es_instructor, login_url='login')
def instructor_fichas(request):

    fichas = InstructorFicha.objects.filter(
        instructor=request.user
    ).select_related('ficha')

    return render(
        request,
        'usuarios/instructor_fichas.html',
        {
            'fichas': fichas
        }
    )


@login_required
@user_passes_test(es_instructor, login_url='login')
def instructor_aulas(request):

    fichas_instructor = InstructorFicha.objects.filter(
        instructor=request.user
    ).values_list(
        'ficha_id',
        flat=True
    )

    aula_ids = FichaAula.objects.filter(
        ficha_id__in=fichas_instructor
    ).values_list(
        'aula_id',
        flat=True
    )

    aulas = Aula.objects.filter(
        id__in=aula_ids
    ).distinct().order_by(
        'nombre'
    )

    return render(
        request,
        'usuarios/instructor_aulas.html',
        {
            'aulas': aulas
        }
    )

@login_required
@user_passes_test(es_instructor, login_url='login')
def instructor_estudiantes(request, ficha_id):

    relacion = get_object_or_404(
        InstructorFicha,
        instructor=request.user,
        ficha_id=ficha_id
    )

    ficha = relacion.ficha

    estudiantes = ficha.aprendices.all().order_by(
        'apellido',
        'nombre'
    )

    return render(
        request,
        'usuarios/instructor_estudiantes.html',
        {
            'ficha': ficha,
            'estudiantes': estudiantes
        }
    )

@login_required
@user_passes_test(es_instructor, login_url='login')
def ficha_aula_instructor(request):

    fichas = InstructorFicha.objects.filter(
        instructor=request.user
    ).select_related(
        'ficha'
    )

    aulas = Aula.objects.filter(
        creado_por=request.user
    )

    relaciones = FichaAula.objects.filter(
        aula__creado_por=request.user
    ).select_related(
        'ficha',
        'aula'
    )

    return render(
        request,
        'usuarios/instructor_ficha_aula.html',
        {
            'fichas': fichas,
            'aulas': aulas,
            'relaciones': relaciones
        }
    )

@login_required
@user_passes_test(es_instructor, login_url='login')
def crear_ficha_aula_instructor(request):

    if request.method == "POST":

        ficha = get_object_or_404(
            InstructorFicha,
            instructor=request.user,
            ficha_id=request.POST.get("ficha")
        )

        aula = get_object_or_404(
            Aula,
            id=request.POST.get("aula"),
            creado_por=request.user
        )

        FichaAula.objects.get_or_create(
            ficha=ficha.ficha,
            aula=aula,
            defaults={
                "jornada": ficha.ficha.jornada
            }
        )

        messages.success(
            request,
            "Relación creada correctamente."
        )

    return redirect(
        "ficha_aula_instructor"
    )

User = get_user_model()

@login_required
@user_passes_test(es_admin, login_url='dashboard') # Cambia el login_url si no es admin para evitar bucles infinitos
def ver_estadisticas_admin(request):
    """
    Vista accesible solo para administradores que calcula el resumen diario.
    """
    hoy = timezone.now().date()
    #Registros de Ingreso Recientes
    registros_recientes = RegistroAsistencia.objects.filter(
        hora_entrada__date=hoy
    ).select_related('usuario').order_by('-hora_entrada')[:5]

    registros_jornada = RegistroAsistencia.objects.filter(
        hora_entrada__date=hoy
    ).select_related(
        'usuario'
    ).prefetch_related(
        'usuario__fichas',
    'usuario__fichas__fichaaula_set__aula'
    ).order_by('-hora_entrada')

    equipos_registrados = Equipo.objects.select_related('estudiante').all()
    
    # Definimos los roles que manejas en el sistema
    roles = ['aprendiz', 'instructor', 'vigilante']
    datos_asistencia = {}
    total_asistencias_dia = 0
    for rol in roles:
        # Total de usuarios registrados con este rol
        total_rol = User.objects.filter(rol=rol, is_active=True).count()
        
        # Usuarios con este rol que tienen al menos un registro hoy
        asistieron_hoy = RegistroAsistencia.objects.filter(
            hora_entrada__date=hoy,
            usuario__rol=rol
        ).values('usuario').distinct().count()

        # Cálculo del porcentaje evitando división por cero
        porcentaje = round((asistieron_hoy / total_rol) * 100) if total_rol > 0 else 0

        total_asistencias_dia += asistieron_hoy

        datos_asistencia[rol] = {
            'total_rol': total_rol,
            'asistieron_hoy': asistieron_hoy,
            'porcentaje': porcentaje,
        }
        

    contexto = {
        'periodo_solicitado': hoy.strftime('%d/%m/%Y'),
        'datos_asistencia': datos_asistencia,
        'total_asistencias_dia': total_asistencias_dia,
        'registros_recientes': registros_recientes,
        'registros_jornada': registros_jornada,
        'equipos_registrados': equipos_registrados,
    }

    # Nota la ruta correcta de la plantilla: 'usuarios/estadisticas.html'
    return render(request, 'usuarios/estadisticas.html', contexto)

@login_required
@require_POST
def generar_token_qr(request):
    # Desactivar anteriores
    TokenQR.objects.filter(usuario=request.user, usado=False).update(usado=True)
    
    # Crear token válido por 5 minutos (300 segundos)
    nuevo_token = TokenQR.objects.create(
        usuario=request.user,
        expira_en=timezone.now() + timedelta(minutes=5)
    )
    
    return JsonResponse({
        'success': True,
        'token_id': str(nuevo_token.id),
        'duracion_segundos': 300
    })

@login_required
def consultar_estado_qr(request, token_id):
    try:
        token = TokenQR.objects.get(id=token_id, usuario=request.user)
        return JsonResponse({'usado': token.usado})
    except TokenQR.DoesNotExist:
        return JsonResponse({'usado': True})


User = get_user_model()

def es_instructor(user):
    return user.is_authenticated and (getattr(user, 'rol', None) in ['instructor', 'INSTRUCTOR'] or user.is_staff)

@login_required
@user_passes_test(es_instructor, login_url='dashboard')
def ver_estudiantes_instructor(request, ficha_id):
    ficha = get_object_or_404(Ficha, id=ficha_id)

    # 1. Obtener la fecha local actual (inicio y fin del día en hora local)
    ahora_local = timezone.localtime(timezone.now())
    inicio_dia = ahora_local.replace(hour=0, minute=0, second=0, microsecond=0)
    fin_dia = ahora_local.replace(hour=23, minute=59, second=59, microsecond=999999)

    # 2. Obtener aprendices pertenecientes a la ficha
    estudiantes = User.objects.filter(
        fichas=ficha, 
        is_active=True
    ).order_by('nombre')

    # 3. Asignar la asistencia de hoy usando el 'related_name' exacto: asistencias
    for estudiante in estudiantes:
        estudiante.registro_hoy = estudiante.asistencias.filter(
            hora_entrada__range=(inicio_dia, fin_dia)
        ).order_by('-hora_entrada').first()

    # 4. Cálculo de estadísticas para las tarjetas superiores
    total_estudiantes = estudiantes.count()
    asistieron = sum(1 for e in estudiantes if e.registro_hoy is not None)
    porcentaje = round((asistieron / total_estudiantes) * 100) if total_estudiantes > 0 else 0

    contexto = {
        'ficha': ficha,
        'estudiantes': estudiantes,
        'periodo_solicitado': ahora_local.strftime('%d/%m/%Y'),
        'datos_asistencia': {
            'aprendiz': {
                'total_rol': total_estudiantes,
                'asistieron_hoy': asistieron,
                'porcentaje': porcentaje,
            }
        }
    }

    return render(request, 'usuarios/estudiantes.html', contexto)
 # Ajusta según tu modelo

User = get_user_model()

@login_required
def exportar_asistencia_csv(request):
    hoy = timezone.now().date()
    
    # 1. Consultar TODOS los usuarios registrados en la base de datos
    usuarios = User.objects.all().prefetch_related(
        'fichas',
        'fichas__fichaaula_set__aula',
        'asistencias'
    ).order_by('apellido', 'nombre')

    # 2. Configurar la respuesta HTTP para descarga CSV
    filename = f"Reporte_Usuarios_Todos_{hoy.strftime('%Y%m%d')}.csv"
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # 3. Incluir BOM (UTF-8) para soporte de tildes y eñes en Excel
    response.write('\ufeff'.encode('utf-8'))

    writer = csv.writer(response)

    # 4. Encabezados del reporte
    headers = [
        "Nombre", 
        "Email", 
        "Documento", 
        "Rol", 
        "Registro",  # Última entrada al sistema hoy (si registró)
        "Teléfono", 
        "Ficha", 
        "Aula", 
        "Jornada"
    ]
    writer.writerow(headers)

    # 5. Iterar sobre todos los usuarios
    for usuario in usuarios:
        # Obtener primera ficha relacionada (si aplica)
        ficha = usuario.fichas.first() if usuario.fichas.exists() else None
        codigo_ficha = ficha.codigo if ficha else "N/A"
        jornada = getattr(ficha, 'jornada', 'N/A') if ficha else "N/A"

        # Obtener aula asociada a la ficha
        aula_nombre = "N/A"
        if ficha and ficha.fichaaula_set.exists():
            ficha_aula = ficha.fichaaula_set.first()
            if ficha_aula.aula:
                aula_nombre = ficha_aula.aula.nombre

        # Buscar si el usuario tiene una asistencia registrada el día de hoy
        asistencia_hoy = usuario.asistencias.filter(
            hora_entrada__date=hoy
        ).order_by('-hora_entrada').first()

        if asistencia_hoy and asistencia_hoy.hora_entrada:
            hora_local = timezone.localtime(asistencia_hoy.hora_entrada)
            momento_registro = hora_local.strftime('%Y-%m-%d %I:%M:%S %p')
        else:
            momento_registro = "Sin registro hoy"

        # Limpieza simple de seguridad contra inyección de fórmulas
        def limpiar(val):
            val_str = str(val or '')
            if val_str.startswith(('=', '+', '-', '@')):
                return f"'{val_str}"
            return val_str

        # Escribir la fila del usuario
        writer.writerow([
            limpiar(f"{usuario.nombre} {usuario.apellido}".strip()),
            limpiar(getattr(usuario, 'email', usuario.username)),
            limpiar(getattr(usuario, 'numeroDocumento', 'N/A')),
            limpiar(usuario.get_rol_display() if hasattr(usuario, 'get_rol_display') else usuario.rol),
            limpiar(momento_registro),
            limpiar(getattr(usuario, 'telefono', 'N/A')),
            limpiar(codigo_ficha),
            limpiar(aula_nombre),
            limpiar(jornada)
        ])

    return response


# ==========================
# AULAS — ADMINISTRADOR
# ==========================

@login_required
@user_passes_test(es_admin, login_url='login')
def dashboard_aulas_admin(request):

    aulas = Aula.objects.all().order_by(
        'nombre'
    )

    return render(
        request,
        'usuarios/dashboard_aulas_admin.html',
        {
            'aulas': aulas
        }
    )


@login_required
@user_passes_test(es_admin, login_url='login')
def crear_aula_admin(request):

    if request.method == 'POST':

        nombre = request.POST.get('nombre')
        bloque = request.POST.get('bloque')
        capacidad = request.POST.get('capacidad')

        Aula.objects.create(
            nombre=nombre,
            bloque=bloque,
            capacidad=capacidad,
            creado_por=request.user
        )

        messages.success(
            request,
            'Aula creada correctamente.'
        )

    return redirect(
        'dashboard_aulas_admin'
    )


@login_required
@user_passes_test(es_admin, login_url='login')
def editar_aula_admin(request, aula_id):

    aula = get_object_or_404(
        Aula,
        id=aula_id
    )

    if request.method == 'POST':

        aula.nombre = request.POST.get('nombre')
        aula.bloque = request.POST.get('bloque')
        aula.capacidad = request.POST.get('capacidad')

        aula.save()

        messages.success(
            request,
            'Aula actualizada correctamente.'
        )

    return redirect(
        'dashboard_aulas_admin'
    )


@login_required
@user_passes_test(es_admin, login_url='login')
def eliminar_aula_admin(request, aula_id):

    aula = get_object_or_404(
        Aula,
        id=aula_id
    )

    if request.method == 'POST':

        aula.delete()

        messages.success(
            request,
            'Aula eliminada correctamente.'
        )

    return redirect(
        'dashboard_aulas_admin'
    )

# ==========================
# FICHA - AULA — ADMINISTRADOR
# ==========================

@login_required
@user_passes_test(es_admin, login_url='login')
def dashboard_ficha_aula_admin(request):

    relaciones = FichaAula.objects.select_related(
        'ficha',
        'aula'
    ).order_by(
        'ficha__codigo'
    )

    fichas = Ficha.objects.all().order_by(
        'codigo'
    )

    aulas = Aula.objects.all().order_by(
        'nombre'
    )

    return render(
        request,
        'usuarios/dashboard_ficha_aula_admin.html',
        {
            'relaciones': relaciones,
            'fichas': fichas,
            'aulas': aulas
        }
    )


@login_required
@user_passes_test(es_admin, login_url='login')
def crear_ficha_aula_admin(request):

    if request.method == 'POST':

        ficha_id = request.POST.get('ficha')
        aula_id = request.POST.get('aula')
        jornada = request.POST.get('jornada')

        ficha = get_object_or_404(
            Ficha,
            id=ficha_id
        )

        aula = get_object_or_404(
            Aula,
            id=aula_id
        )

        if FichaAula.objects.filter(
            ficha=ficha,
            aula=aula
        ).exists():

            messages.error(
                request,
                'Esta ficha ya está relacionada con esta aula.'
            )

            return redirect(
                'dashboard_ficha_aula_admin'
            )

        FichaAula.objects.create(
            ficha=ficha,
            aula=aula,
            jornada=jornada
        )

        messages.success(
            request,
            'Relación Ficha - Aula creada correctamente.'
        )

    return redirect(
        'dashboard_ficha_aula_admin'
    )


@login_required
@user_passes_test(es_admin, login_url='login')
def editar_ficha_aula_admin(request, relacion_id):

    relacion = get_object_or_404(
        FichaAula,
        id=relacion_id
    )

    if request.method == 'POST':

        ficha = get_object_or_404(
            Ficha,
            id=request.POST.get('ficha')
        )

        aula = get_object_or_404(
            Aula,
            id=request.POST.get('aula')
        )

        jornada = request.POST.get('jornada')

        relacion.ficha = ficha
        relacion.aula = aula
        relacion.jornada = jornada

        relacion.save()

        messages.success(
            request,
            'Relación Ficha - Aula actualizada correctamente.'
        )

    return redirect(
        'dashboard_ficha_aula_admin'
    )


@login_required
@user_passes_test(es_admin, login_url='login')
def eliminar_ficha_aula_admin(request, relacion_id):

    relacion = get_object_or_404(
        FichaAula,
        id=relacion_id
    )

    if request.method == 'POST':

        relacion.delete()

        messages.success(
            request,
            'Relación Ficha - Aula eliminada correctamente.'
        )

    return redirect(
        'dashboard_ficha_aula_admin'
    )