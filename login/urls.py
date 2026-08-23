from django.urls import path
from . import views

app_name = 'login'

urlpatterns = [
    path('admin-login/', views.admin_login, name='admin_login'),
    path('configurar-admin/', views.configurar_admin, name='configurar_admin'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.admin_logout, name='logout'),
    path('gestionar-propiedades/', views.gestionar_propiedades, name='gestionar_propiedades'),
    path('editar-propiedad/<int:propiedad_id>/', views.editar_propiedad, name='editar_propiedad'),
    path('eliminar-propiedad/<int:propiedad_id>/', views.eliminar_propiedad, name='eliminar_propiedad'),
    path('eliminar-propiedad-ajax/<int:propiedad_id>/', views.eliminar_propiedad_ajax, name='eliminar_propiedad_ajax'),
    path('actualizar-perfil/', views.actualizar_perfil, name='actualizar_perfil'),
    path('crear-nuevo-usuario-admin/', views.crear_nuevo_usuario_admin, name='crear_nuevo_usuario_admin'),
    path('contar-usuarios-admin/', views.contar_usuarios_admin, name='contar_usuarios_admin'),
    path('cambiar-password/', views.cambiar_password, name='cambiar_password'),
    path('enviar-codigo-sms/', views.enviar_codigo_sms, name='enviar_codigo_sms'),
    path('verificar-codigo-sms/', views.verificar_codigo_sms, name='verificar_codigo_sms'),
    path('listar-usuarios-admin/', views.listar_usuarios_admin, name='listar_usuarios_admin'),
    path('eliminar-usuario-admin/<int:usuario_id>/', views.eliminar_usuario_admin, name='eliminar_usuario_admin'),
    path('gestionar-resenas/', views.gestionar_resenas, name='gestionar_resenas'),
    path('aprobar-resena/<int:resena_id>/', views.aprobar_resena, name='aprobar_resena'),
    path('rechazar-resena/<int:resena_id>/', views.rechazar_resena, name='rechazar_resena'),
    path('eliminar-resena/', views.eliminar_resena, name='eliminar_resena'),
    path('dashboard-clicks-data/', views.dashboard_clicks_data, name='dashboard_clicks_data'),
    
    # URLs para 2FA
    path('setup-2fa/', views.setup_2fa, name='setup_2fa'),
    path('disable-2fa/', views.disable_2fa, name='disable_2fa'),
    path('2fa-success/', views.two_factor_success, name='2fa_success'),
    
    # URLs para recuperación de contraseña
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset-verify/<str:email>/', views.password_reset_verify, name='password_reset_verify'),
]
