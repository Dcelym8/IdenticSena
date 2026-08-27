from django.urls import path
from . import views

urlpatterns = [

    path('registro/', views.registro, name='registro'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('inicio/', views.inicio_view, name='inicio'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('dashboard/usuarios/', views.dashboard_usuarios, name='dashboard_usuarios'),

    path('api/generar-qr/', views.generar_token_qr, name='generar_token_qr'),
path('api/estado-qr/<str:token_id>/', views.consultar_estado_qr, name='consultar_estado_qr'),

     path('estadisticas/', 
             views.ver_estadisticas_admin, 
             name='estadisticas'),



    path('dashboard/usuarios/crear/',
         views.crear_usuario,
         name='crear_usuario'),

    path('dashboard/usuarios/<int:user_id>/editar/',
         views.editar_usuario,
         name='editar_usuario'),

    path('dashboard/usuarios/<int:user_id>/eliminar/',
         views.eliminar_usuario,
         name='eliminar_usuario'),

    path('dashboard/usuarios/<int:user_id>/toggle/',
         views.dashboard_toggle,
         name='dashboard_toggle'),

    path('dashboard/usuarios/<int:user_id>/rol/',
         views.dashboard_editar_rol,
         name='dashboard_editar_rol'),

    path(
        'dashboard/permisos/',
        views.dashboard_permisos,
        name='dashboard_permisos'
    ),

    path(
        'dashboard/permisos/<str:rol>/guardar/',
        views.dashboard_permisos_guardar,
        name='dashboard_permisos_guardar'
    ),

    path(
        'equipos/',
        views.gestionar_equipos,
        name='gestionar_equipos'
    ),

    path(
        'equipos/eliminar/<int:equipo_id>/',
        views.eliminar_equipo,
        name='eliminar_equipo'
    ),

    path(
        'dashboard/vigilante/',
        views.panel_vigilante,
        name='panel_vigilante'
    ),

    path(
        'dashboard/vigilante/verificar/<str:token>/',
        views.verificar_aprendiz_simple,
        name='verificar_qr'
    ),

    path(
        'dashboard/instructor/',
        views.dashboard_instructor,
        name='dashboard_instructor'
    ),

    path(
        'dashboard/fichas/',
        views.dashboard_fichas,
        name='dashboard_fichas'
    ),

    path(
        'dashboard/fichas/crear/',
        views.crear_ficha,
        name='crear_ficha'
    ),

    path(
        'dashboard/fichas/<int:ficha_id>/editar/',
        views.editar_ficha,
        name='editar_ficha'
    ),

    path(
        'dashboard/fichas/<int:ficha_id>/eliminar/',
        views.eliminar_ficha,
        name='eliminar_ficha'
    ),

     path(
          'dashboard/asignaciones/',
          views.dashboard_asignar_fichas,
          name='dashboard_asignaciones'
     ),

    path(
        'dashboard/asignaciones/crear/',
        views.crear_asignacion_ficha,
        name='crear_asignacion'
    ),

    path(
        'dashboard/asignaciones/<int:asignacion_id>/eliminar/',
        views.eliminar_asignacion_ficha,
        name='eliminar_asignacion'
    ),

    path(
        'dashboard/aulas/',
        views.dashboard_aulas,
        name='dashboard_aulas'
    ),

    path(
        'dashboard/aulas/crear/',
        views.crear_aula,
        name='crear_aula'
    ),

    path(
        'dashboard/aulas/<int:aula_id>/editar/',
        views.editar_aula,
        name='editar_aula'
    ),

    path(
        'dashboard/aulas/<int:aula_id>/eliminar/',
        views.eliminar_aula,
        name='eliminar_aula'
    ),

    path(
        'dashboard/ficha-aula/',
        views.dashboard_ficha_aula,
        name='dashboard_ficha_aula'
    ),

    path(
        'dashboard/ficha-aula/crear/',
        views.crear_ficha_aula,
        name='crear_ficha_aula'
    ),

    path(
        'dashboard/ficha-aula/<int:relacion_id>/editar/',
        views.editar_ficha_aula,
        name='editar_ficha_aula'
    ),

    path(
        'dashboard/ficha-aula/<int:relacion_id>/eliminar/',
        views.eliminar_ficha_aula,
        name='eliminar_ficha_aula'
    ),

    path(
          'dashboard/fichas/',
          views.dashboard_fichas,
          name='dashboard_fichas'
     ),

     path(
          'dashboard/fichas/crear/',
          views.crear_ficha,
          name='crear_ficha'
     ),

     path(
          'dashboard/fichas/<int:ficha_id>/editar/',
          views.editar_ficha,
          name='editar_ficha'
     ),

     path(
          'dashboard/fichas/<int:ficha_id>/eliminar/',
          views.eliminar_ficha,
          name='eliminar_ficha'
     ),

     path(
          'dashboard/instructor/',
          views.panel_instructor,
          name='panel_instructor'
     ),


     path(
          'dashboard/aulas/',
          views.dashboard_aulas,
          name='dashboard_aulas'
     ),


     path(
          'dashboard/aulas/crear/',
          views.crear_aula,
          name='crear_aula'
     ),


     path(
          'dashboard/aulas/<int:aula_id>/editar/',
          views.editar_aula,
          name='editar_aula'
     ),


     path(
          'dashboard/aulas/<int:aula_id>/eliminar/',
          views.eliminar_aula,
          name='eliminar_aula'
     ),  

     path(
          'dashboard/asignar-fichas/',
          views.dashboard_asignar_fichas,
          name='dashboard_asignar_fichas'
     ),

     path(
          'dashboard/asignar-fichas/crear/',
          views.crear_asignacion_ficha,      
          name='crear_asignacion_ficha',
     ),

     path(
          'dashboard/asignar-fichas/eliminar/<int:asignacion_id>/',
          views.eliminar_asignacion_ficha,
          name='eliminar_asignacion_ficha'
     ),


     path(
            'dashboard/instructor/fichas/',
            views.instructor_fichas,
            name='instructor_fichas'
     ),

     path(
            'dashboard/instructor/fichas/',
            views.instructor_fichas,
            name='instructor_fichas'
    ),

    path(
            'dashboard/instructor/aulas/',
            views.instructor_aulas,
            name='instructor_aulas'
    ),

    path(
            'dashboard/instructor/ficha-aula/',
            views.ficha_aula_instructor,
            name='ficha_aula_instructor'
    ),

    path(
            'dashboard/instructor/ficha/<int:ficha_id>/estudiantes/',
            views.instructor_estudiantes,
            name='instructor_estudiantes'
    ),

    path(
            'dashboard/instructor/ficha-aula/crear/',
            views.crear_ficha_aula_instructor,
            name='crear_ficha_aula_instructor'
    ),

    path(
        'dashboard/instructor/ficha/<int:ficha_id>/estudiantes/', 
        views.ver_estudiantes_instructor, 
        name='instructor_estudiantes_ficha'
    ),

    path(
        'estadisticas/exportar-csv/', 
        views.exportar_asistencia_csv, 
        name='exportar_asistencia_csv'),

    path(
        'dashboard/admin/aulas/',
        views.dashboard_aulas_admin,
        name='dashboard_aulas_admin'
    ),

    path(
        'dashboard/admin/aulas/crear/',
        views.crear_aula_admin,
        name='crear_aula_admin'
    ),

    path(
        'dashboard/admin/aulas/<int:aula_id>/editar/',
        views.editar_aula_admin,
        name='editar_aula_admin'
    ),

    path(
        'dashboard/admin/aulas/<int:aula_id>/eliminar/',
        views.eliminar_aula_admin,
        name='eliminar_aula_admin'
    ),

    path(
        'dashboard/admin/ficha-aula/',
        views.dashboard_ficha_aula_admin,
        name='dashboard_ficha_aula_admin'
    ),

    path(
        'dashboard/admin/ficha-aula/crear/',
        views.crear_ficha_aula_admin,
        name='crear_ficha_aula_admin'
    ),

    path(
        'dashboard/admin/ficha-aula/<int:relacion_id>/editar/',
        views.editar_ficha_aula_admin,
        name='editar_ficha_aula_admin'
    ),

    path(
        'dashboard/admin/ficha-aula/<int:relacion_id>/eliminar/',
        views.eliminar_ficha_aula_admin,
        name='eliminar_ficha_aula_admin'
    ),
]