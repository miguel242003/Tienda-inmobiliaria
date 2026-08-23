from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

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
            password="ClaveSegura123!",
            activo=True,
        )

        response = self.client.get(reverse("login:admin_login"))
        self.assertEqual(response.status_code, 200)


class AdminCredentialsModelTests(TestCase):
    def test_password_se_guarda_encriptada(self):
        user = User.objects.create_user(username="admin2", password="otra_clave")
        credenciales = AdminCredentials.objects.create(
            user=user,
            email="admin2@example.com",
            password="ClaveEnTextoPlano",
        )

        self.assertNotEqual(credenciales.password, "ClaveEnTextoPlano")
        self.assertTrue(check_password("ClaveEnTextoPlano", credenciales.password))
