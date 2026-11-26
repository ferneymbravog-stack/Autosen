"""Migración de datos: enlaza registros existentes de auditoría con su Usuario por correo."""
from django.db import migrations


def enlazar_auditoria_con_usuarios(apps, schema_editor):
    Usuario = apps.get_model("core", "Usuario")
    RegistroAuditoria = apps.get_model("core", "RegistroAuditoria")

    por_correo: dict[str, int] = {}
    for u in Usuario.objects.all():
        if u.correo and u.correo.strip():
            clave = u.correo.strip().lower()
            por_correo.setdefault(clave, u.pk)

    enlazados = 0
    for reg in RegistroAuditoria.objects.filter(usuario__isnull=True):
        correo = (reg.usuario_correo or "").strip().lower()
        uid = por_correo.get(correo)
        if uid is not None:
            RegistroAuditoria.objects.filter(pk=reg.pk).update(usuario_id=uid)
            enlazados += 1

    print(f"  [0012] Registros de auditoría enlazados a usuario: {enlazados}.")


def desenlazar_auditoria_usuarios(apps, schema_editor):
    RegistroAuditoria = apps.get_model("core", "RegistroAuditoria")
    RegistroAuditoria.objects.all().update(usuario_id=None)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_registroauditoria_usuario"),
    ]

    operations = [
        migrations.RunPython(enlazar_auditoria_con_usuarios, desenlazar_auditoria_usuarios),
    ]
