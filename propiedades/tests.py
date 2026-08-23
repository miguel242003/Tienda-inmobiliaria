from django.test import TestCase
from django.urls import reverse

from .models import Propiedad, Resena


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
