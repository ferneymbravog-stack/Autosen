"""Migración de esquema: añade usuario ForeignKey(Usuario, SET_NULL) a RegistroAuditoria."""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_fk_vehiculo_en_lecturas_y_alertas"),
    ]

    operations = [
        migrations.AddField(
            model_name="registroauditoria",
            name="usuario",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="registros_auditoria",
                to="core.usuario",
            ),
        ),
    ]
