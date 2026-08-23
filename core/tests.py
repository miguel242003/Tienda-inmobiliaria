from django.test import TestCase
from django.urls import reverse

from .models import ContactSubmission


class CoreViewTests(TestCase):
    def test_home_responde_200(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)

    def test_contact_get_responde_200(self):
        response = self.client.get(reverse("core:contact"))
        self.assertEqual(response.status_code, 200)


class ContactSubmissionModelTests(TestCase):
    def test_str_incluye_nombre_y_asunto(self):
        envio = ContactSubmission.objects.create(
            nombre="Maria Lopez",
            email="maria@example.com",
            asunto="consulta_general",
            mensaje="Quisiera mas informacion.",
        )
        self.assertIn("Maria Lopez", str(envio))
        self.assertIn("Consulta General", str(envio))
