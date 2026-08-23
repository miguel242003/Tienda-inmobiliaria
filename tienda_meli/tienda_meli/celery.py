"""
Configuración de Celery para tareas en background (conversión de imágenes a
WebP, etc.) que no deben bloquear el ciclo request/response.

En desarrollo y en tests, CELERY_TASK_ALWAYS_EAGER hace que las tareas se
ejecuten de forma síncrona en el mismo proceso, sin necesitar un broker ni un
worker corriendo. En producción, hace falta:
  1. Un broker (se reutiliza REDIS_URL / CELERY_BROKER_URL).
  2. Un proceso worker corriendo: `celery -A tienda_meli.tienda_meli worker -l info`
"""
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda_meli.tienda_meli.settings')

app = Celery('tienda_meli')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
