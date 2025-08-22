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
]
