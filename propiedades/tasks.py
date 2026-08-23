import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(name='propiedades.convertir_imagenes_a_webp')
def convertir_imagenes_propiedad_a_webp(
    propiedad_id,
    imagen_principal_original=None,
    imagen_secundaria_original=None,
    imagen_principal_existia=False,
    imagen_secundaria_existia=False,
):
    """Convierte a WebP y copia a static las imágenes principal/secundaria de
    una propiedad. Se ejecuta en background (Celery) para no bloquear el
    request que crea o edita la propiedad.

    Recibe el `pk` en vez de la instancia porque las tareas de Celery se
    serializan (JSON) y pueden correr en otro proceso: hay que releer el
    objeto desde la base de datos.
    """
    from django.core.files.storage import default_storage
    from core.utils import copiar_imagen_a_static
    from .models import Propiedad

    try:
        propiedad = Propiedad.objects.get(pk=propiedad_id)
    except Propiedad.DoesNotExist:
        logger.warning(f"convertir_imagenes_propiedad_a_webp: la propiedad {propiedad_id} ya no existe")
        return

    def _convertir(imagen_field, nombre_original, existia, etiqueta):
        if not imagen_field:
            return
        if not default_storage.exists(imagen_field.name):
            logger.error(f"Imagen {etiqueta} no encontrada en storage: {imagen_field.name}")
            return

        cambio = not nombre_original or imagen_field.name != nombre_original
        if not (cambio or not existia):
            return

        nombre_archivo = f"{propiedad.slug}-{etiqueta}"
        try:
            resultado = copiar_imagen_a_static(imagen_field, nombre_archivo, quality=85)
            if resultado is not None:
                logger.info(f"Imagen {etiqueta} convertida y copiada a static: {resultado}")
            else:
                logger.error(f"copiar_imagen_a_static no devolvió resultado para {imagen_field.name}")
        except Exception as e:
            logger.error(f"Excepción al convertir imagen {etiqueta} a WebP: {e}", exc_info=True)

    _convertir(propiedad.imagen_principal, imagen_principal_original, imagen_principal_existia, 'principal')
    _convertir(propiedad.imagen_secundaria, imagen_secundaria_original, imagen_secundaria_existia, 'secundaria')
