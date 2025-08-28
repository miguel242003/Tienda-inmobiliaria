from django.urls import path
from . import views

app_name = 'propiedades'

urlpatterns = [
    path('', views.lista_propiedades, name='lista'),
    path('crear/', views.crear_propiedad, name='crear'),
    path('<int:propiedad_id>/', views.detalle_propiedad, name='detalle'),
    path('buscar/', views.buscar_propiedades, name='buscar'),
    path('upload-fotos/', views.upload_fotos_adicionales, name='upload_fotos'),
]
