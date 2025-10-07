from django.urls import path
from . import views

app_name = 'propiedades'

urlpatterns = [
    path('', views.lista_propiedades, name='lista'),
    path('crear/', views.crear_propiedad, name='crear'),
    path('<slug:slug>/', views.detalle_propiedad, name='detalle'),
    path('buscar/', views.lista_propiedades, name='buscar'),  # Ahora redirige a la misma vista
    path('upload-fotos/', views.upload_fotos_adicionales, name='upload_fotos'),
    path('registrar-click/', views.registrar_click, name='registrar_click'),
    path('<slug:slug>/crear-resena/', views.crear_resena, name='crear_resena'),
]
