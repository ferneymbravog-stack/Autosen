"""Migración de esquema: convierte Id_vehiculo en ForeignKey(Vehiculo, SET_NULL) conservando columna y datos."""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_limpiar_huerfanos_y_placa_historica"),
    ]

    operations = [
        migrations.RenameField(
            model_name="lectura",
            old_name="id_vehiculo",
            new_name="vehiculo",
        ),
        migrations.AlterField(
            model_name="lectura",
            name="vehiculo",
            field=models.ForeignKey(
                blank=True,
                db_column="Id_vehiculo",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="lecturas",
                to="core.vehiculo",
            ),
        ),
        migrations.RenameField(
            model_name="alerta",
            old_name="id_vehiculo",
            new_name="vehiculo",
        ),
        migrations.AlterField(
            model_name="alerta",
            name="vehiculo",
            field=models.ForeignKey(
                blank=True,
                db_column="Id_vehiculo",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="alertas",
                to="core.vehiculo",
            ),
        ),
    ]
