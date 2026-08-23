from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from propiedades.models import Propiedad

from .models import AdminCredentials


class DashboardAccessTests(TestCase):
    def test_dashboard_redirige_a_login_si_no_hay_sesion(self):
        response = self.client.get(reverse("login:dashboard"))
        self.assertEqual(response.status_code, 302)


class AdminLoginViewTests(TestCase):
    def test_redirige_a_configurar_admin_si_no_hay_credenciales(self):
        response = self.client.get(reverse("login:admin_login"))
        self.assertRedirects(response, reverse("login:configurar_admin"))

    def test_responde_200_si_ya_hay_credenciales_configuradas(self):
        user = User.objects.create_user(username="admin", password="ClaveSegura123!")
        AdminCredentials.objects.create(
            user=user,
            email="admin@example.com",
            activo=True,
        )

        response = self.client.get(reverse("login:admin_login"))
        self.assertEqual(response.status_code, 200)


class ConfigurarAdminViewTests(TestCase):
    """Cubre el flujo de bootstrap (primer admin del sistema), tocado al
    quitarle el campo `password` a AdminCredentials."""

    def test_post_valido_crea_user_y_admincredentials_vinculados(self):
        response = self.client.post(
            reverse("login:configurar_admin"),
            {
                "nombre": "Ana",
                "apellido": "Gomez",
                "email": "bootstrap@example.com",
                "telefono": "+541122334455",
                "password": "ClaveSegura123!",
                "confirmar_password": "ClaveSegura123!",
            },
        )
        self.assertRedirects(response, reverse("login:admin_login"))

        user = User.objects.get(username="bootstrap@example.com")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)  # el primer admin sí es superusuario
        self.assertTrue(user.check_password("ClaveSegura123!"))

        credenciales = AdminCredentials.objects.get(email="bootstrap@example.com")
        self.assertEqual(credenciales.user, user)
        self.assertTrue(credenciales.check_password("ClaveSegura123!"))

    def test_no_permite_configurar_dos_veces(self):
        user = User.objects.create_user(username="ya_existe", password="ClaveSegura123!")
        AdminCredentials.objects.create(user=user, email="ya@example.com", activo=True)

        response = self.client.get(reverse("login:configurar_admin"))
        self.assertRedirects(response, reverse("login:admin_login"))


class AdminCredentialsModelTests(TestCase):
    """AdminCredentials ya no guarda su propio hash de contraseña: la
    contraseña vive únicamente en auth.User, y check_password() delega ahí."""

    def test_check_password_delega_en_el_user_vinculado(self):
        user = User.objects.create_user(username="admin2", password="ClaveSegura123!")
        credenciales = AdminCredentials.objects.create(
            user=user,
            email="admin2@example.com",
        )

        self.assertTrue(credenciales.check_password("ClaveSegura123!"))
        self.assertFalse(credenciales.check_password("otra-cosa"))


class CrearNuevoUsuarioAdminTests(TestCase):
    """Un admin creado desde el dashboard no debía quedar como superusuario de
    Django (ver hallazgo crítico #4 de la revisión de seguridad)."""

    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="staff@example.com", password="ClaveSegura123!", is_staff=True
        )
        self.client.login(username="staff@example.com", password="ClaveSegura123!")

    def test_nuevo_admin_no_es_superusuario(self):
        response = self.client.post(
            reverse("login:crear_nuevo_usuario_admin"),
            {
                "nombre": "Juan",
                "apellido": "Perez",
                "telefono": "+541122334455",
                "email": "nuevo.admin@example.com",
                "password": "ClaveSegura123!",
                "confirmar_password": "ClaveSegura123!",
            },
        )

        data = response.json()
        self.assertTrue(data.get("success"), data)

        nuevo_usuario = User.objects.get(username="nuevo.admin@example.com")
        self.assertTrue(nuevo_usuario.is_staff)
        self.assertFalse(nuevo_usuario.is_superuser)


class EditarPropiedadViewTests(TestCase):
    """Smoke tests para editar_propiedad tras separarla en funciones más chicas."""

    def setUp(self):
        self.staff = User.objects.create_user(
            username="staff_edita", password="ClaveSegura123!", is_staff=True
        )
        self.client.login(username="staff_edita", password="ClaveSegura123!")
        self.propiedad = Propiedad.objects.create(
            titulo="Departamento Original",
            descripcion="Descripción original de prueba.",
            precio=100000,
            tipo="apartamento",
            operacion="venta",
            ubicacion="Calle Falsa 123",
            metros_cuadrados=80,
        )

    def _datos_validos(self, **extra):
        datos = {
            "titulo": "Departamento Editado",
            "descripcion": "Descripción editada con más de diez caracteres.",
            "precio": "120000",
            "tipo": "apartamento",
            "operacion": "venta",
            "estado": "disponible",
            "ubicacion": "Calle Falsa 123",
            "metros_cuadrados": "85",
            "habitaciones": "2",
            "banos": "1",
            "ambientes": "3",
        }
        datos.update(extra)
        return datos

    def test_requiere_login(self):
        self.client.logout()
        response = self.client.get(
            reverse("login:editar_propiedad", kwargs={"propiedad_id": self.propiedad.id})
        )
        self.assertEqual(response.status_code, 302)

    def test_get_muestra_formulario_con_datos_actuales(self):
        response = self.client.get(
            reverse("login:editar_propiedad", kwargs={"propiedad_id": self.propiedad.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Departamento Original")

    def test_post_valido_actualiza_propiedad_y_redirige(self):
        response = self.client.post(
            reverse("login:editar_propiedad", kwargs={"propiedad_id": self.propiedad.id}),
            self._datos_validos(),
        )
        self.assertRedirects(response, reverse("login:dashboard"))
        self.propiedad.refresh_from_db()
        self.assertEqual(self.propiedad.titulo, "Departamento Editado")
        self.assertEqual(self.propiedad.metros_cuadrados, 85)

    def test_post_ajax_valido_responde_json_success(self):
        response = self.client.post(
            reverse("login:editar_propiedad", kwargs={"propiedad_id": self.propiedad.id}),
            self._datos_validos(),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        data = response.json()
        self.assertTrue(data["success"])

    def test_post_invalido_no_actualiza_propiedad(self):
        response = self.client.post(
            reverse("login:editar_propiedad", kwargs={"propiedad_id": self.propiedad.id}),
            self._datos_validos(precio="-10"),
        )
        self.assertEqual(response.status_code, 200)
        self.propiedad.refresh_from_db()
        self.assertEqual(self.propiedad.titulo, "Departamento Original")
