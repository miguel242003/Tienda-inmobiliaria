# Generado por Django 5.2.1 el 2025-08-22 03:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='admincredentials',
            name='direccion',
        ),
        migrations.RemoveField(
            model_name='admincredentials',
            name='nombre_empresa',
        ),
        migrations.RemoveField(
            model_name='admincredentials',
            name='telefono',
        ),
    ]
