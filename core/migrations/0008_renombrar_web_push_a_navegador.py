"""Migración de datos: renombra el canal WEB_PUSH a NAVEGADOR en NotificacionEnviada."""
from django.db import migrations


def renombrar_a_navegador(apps, schema_editor):
    NotificacionEnviada = apps.get_model("core", "NotificacionEnviada")
    NotificacionEnviada.objects.filter(canal="WEB_PUSH").update(canal="NAVEGADOR")


def revertir_a_web_push(apps, schema_editor):
    NotificacionEnviada = apps.get_model("core", "NotificacionEnviada")
    NotificacionEnviada.objects.filter(canal="NAVEGADOR").update(canal="WEB_PUSH")


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_notificacionenviada_detalle_error"),
    ]

    operations = [
        migrations.RunPython(renombrar_a_navegador, revertir_a_web_push),
    ]
