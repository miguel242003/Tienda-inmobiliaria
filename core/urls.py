from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('consorcio/', views.consorcio, name='consorcio'),
    path('cv/', views.cv, name='cv'),
]
