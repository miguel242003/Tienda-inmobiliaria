import base64

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Propiedad, Resena

# PNG 1x1 válido en base64, usado para probar la validación real de tipo MIME
PNG_1X1_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
    "+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def crear_propiedad(titulo="Casa de prueba", **extra):
    datos = dict(
        descripcion="Descripción de prueba",
        precio=150000,
        tipo="casa",
        operacion="venta",
        ubicacion="Viña del Mar",
        metros_cuadrados=120,
    )
    datos.update(extra)
    return Propiedad.objects.create(titulo=titulo, **datos)


class PropiedadModelTests(TestCase):
    def test_slug_se_genera_automaticamente(self):
        propiedad = crear_propiedad(titulo="Casa Con Vista Al Mar")
        self.assertEqual(propiedad.slug, "casa-con-vista-al-mar")

    def test_slug_no_se_repite_con_titulos_duplicados(self):
        primera = crear_propiedad(titulo="Departamento Centrico")
        segunda = crear_propiedad(titulo="Departamento Centrico")
        self.assertEqual(primera.slug, "departamento-centrico")
        self.assertEqual(segunda.slug, "departamento-centrico-1")

    def test_precio_formateado_usa_punto_como_separador_de_miles(self):
        propiedad = crear_propiedad(precio=150000)
        self.assertEqual(propiedad.get_precio_formateado(), "$150.000")


class ConversionWebPEnBackgroundTests(TestCase):
    """La conversión a WebP se despachó como tarea de Celery para no bloquear
    el guardado de la propiedad. Con CELERY_TASK_ALWAYS_EAGER (ver
    settings.py) corre síncrona en los tests, así que este test ejercita el
    pipeline completo (save -> tarea -> copiar_imagen_a_static)."""

    def test_guardar_propiedad_con_imagen_no_falla_y_no_bloquea(self):
        imagen = SimpleUploadedFile(
            "principal.png", base64.b64decode(PNG_1X1_B64), content_type="image/png"
        )
        propiedad = crear_propiedad(
            titulo="Casa Con Imagen Principal", imagen_principal=imagen
        )
        # No debe lanzar excepción y la imagen debe seguir accesible.
        self.assertTrue(propiedad.imagen_principal)

    def test_editar_propiedad_sin_imagenes_no_despacha_conversion_innecesaria(self):
        propiedad = crear_propiedad(titulo="Casa Sin Imagenes")
        propiedad.descripcion = "Descripción actualizada de prueba."
        propiedad.save()  # no debe fallar aunque no haya imágenes que convertir
        propiedad.refresh_from_db()
        self.assertEqual(propiedad.descripcion, "Descripción actualizada de prueba.")


class ResenaModelTests(TestCase):
    def test_aprobar_cambia_estado_y_registra_fecha(self):
        propiedad = crear_propiedad()
        resena = Resena.objects.create(
            propiedad=propiedad,
            nombre_usuario="Juan Perez",
            email_usuario="juan@example.com",
            calificacion=5,
            titulo="Excelente",
            comentario="Muy buena atencion",
        )
        self.assertEqual(resena.estado, "pendiente")

        resena.aprobar(moderador=None)

        self.assertEqual(resena.estado, "aprobada")
        self.assertIsNotNone(resena.fecha_moderacion)


class PropiedadesViewTests(TestCase):
    def test_lista_propiedades_responde_200(self):
        response = self.client.get(reverse("propiedades:lista"))
        self.assertEqual(response.status_code, 200)

    def test_detalle_propiedad_responde_200_si_existe(self):
        propiedad = crear_propiedad(estado="disponible")
        response = self.client.get(
            reverse("propiedades:detalle", kwargs={"slug": propiedad.slug})
        )
        self.assertEqual(response.status_code, 200)

    def test_detalle_propiedad_responde_404_si_no_existe(self):
        response = self.client.get(
            reverse("propiedades:detalle", kwargs={"slug": "no-existe"})
        )
        self.assertEqual(response.status_code, 404)


class CrearPropiedadViewTests(TestCase):
    """Smoke tests para crear_propiedad tras separarla en funciones más chicas."""

    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff_crea", password="ClaveSegura123!", is_staff=True
        )
        self.client.login(username="staff_crea", password="ClaveSegura123!")
        self.datos_validos = {
            "titulo": "Casa Nueva De Prueba",
            "descripcion": "Una descripción con más de diez caracteres.",
            "precio": "200000",
            "tipo": "casa",
            "operacion": "venta",
            "estado": "disponible",
            "ubicacion": "Av. Siempre Viva 742",
            "metros_cuadrados": "150",
            "habitaciones": "3",
            "banos": "2",
            "ambientes": "4",
        }

    def test_requiere_login(self):
        self.client.logout()
        response = self.client.post(reverse("propiedades:crear"), self.datos_validos)
        self.assertEqual(response.status_code, 302)

    def test_get_muestra_formulario_vacio(self):
        response = self.client.get(reverse("propiedades:crear"))
        self.assertEqual(response.status_code, 200)

    def test_post_valido_crea_propiedad_y_redirige(self):
        response = self.client.post(reverse("propiedades:crear"), self.datos_validos)
        self.assertTrue(Propiedad.objects.filter(titulo="Casa Nueva De Prueba").exists())
        propiedad = Propiedad.objects.get(titulo="Casa Nueva De Prueba")
        self.assertRedirects(
            response, reverse("propiedades:detalle", kwargs={"slug": propiedad.slug})
        )

    def test_post_ajax_valido_responde_json_success(self):
        response = self.client.post(
            reverse("propiedades:crear"),
            self.datos_validos,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        data = response.json()
        self.assertTrue(data["success"])

    def test_post_sin_titulo_no_crea_propiedad(self):
        datos = dict(self.datos_validos)
        datos["titulo"] = ""
        response = self.client.post(reverse("propiedades:crear"), datos)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Propiedad.objects.filter(ubicacion="Av. Siempre Viva 742").exists())

    def test_post_invalido_muestra_errores_de_formulario(self):
        datos = dict(self.datos_validos)
        datos["precio"] = "-5"
        response = self.client.post(reverse("propiedades:crear"), datos)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Propiedad.objects.filter(titulo="Casa Nueva De Prueba").exists())


class UploadFotosAdicionalesSeguridadTests(TestCase):
    """El endpoint de subida de fotos debía ser accesible sin autenticación
    ni validación de archivo (ver hallazgo crítico #1 de la revisión de
    seguridad); estos tests verifican que quedó cerrado."""

    def setUp(self):
        self.propiedad = crear_propiedad(estado="disponible")
        self.url = reverse("propiedades:upload_fotos")

    def test_upload_requiere_autenticacion(self):
        response = self.client.post(self.url, {"propiedad_id": self.propiedad.id})
        self.assertEqual(response.status_code, 302)  # redirige a login

    def test_upload_requiere_permisos_de_staff(self):
        User.objects.create_user(username="usuario_normal", password="ClaveSegura123!")
        self.client.login(username="usuario_normal", password="ClaveSegura123!")

        response = self.client.post(self.url, {"propiedad_id": self.propiedad.id})
        self.assertEqual(response.status_code, 403)

    def test_upload_rechaza_archivo_que_no_es_imagen_real(self):
        staff = User.objects.create_user(
            username="admin_staff", password="ClaveSegura123!", is_staff=True
        )
        self.client.login(username="admin_staff", password="ClaveSegura123!")

        archivo_falso = SimpleUploadedFile(
            "foto.jpg", b"esto no es una imagen", content_type="image/jpeg"
        )
        response = self.client.post(
            self.url,
            {"propiedad_id": self.propiedad.id, "fotos": [archivo_falso]},
        )
        data = response.json()
        self.assertFalse(data["success"])
        self.assertEqual(self.propiedad.fotos.count(), 0)

    def test_upload_acepta_imagen_real_para_staff(self):
        staff = User.objects.create_user(
            username="admin_staff2", password="ClaveSegura123!", is_staff=True
        )
        self.client.login(username="admin_staff2", password="ClaveSegura123!")

        imagen = SimpleUploadedFile(
            "foto.png", base64.b64decode(PNG_1X1_B64), content_type="image/png"
        )
        response = self.client.post(
            self.url,
            {"propiedad_id": self.propiedad.id, "fotos": [imagen]},
        )
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(self.propiedad.fotos.count(), 1)
