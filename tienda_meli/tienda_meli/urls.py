"""
Configuración de URL para el proyecto tienda_meli.

La lista `urlpatterns` enruta URLs a vistas. Para más información ver:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Ejemplos:
Vistas de función
    1. Agregar un import:  from my_app import views
    2. Agregar una URL a urlpatterns:  path('', views.home, name='home')
Vistas basadas en clase
    1. Agregar un import:  from other_app.views import Home
    2. Agregar una URL a urlpatterns:  path('', Home.as_view(), name='home')
Incluir otra URLconf
    1. Importar la función include(): from django.urls import include, path
    2. Agregar una URL a urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('propiedades/', include('propiedades.urls')),
    path('login/', include('login.urls')),
]

# Configuración para archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
