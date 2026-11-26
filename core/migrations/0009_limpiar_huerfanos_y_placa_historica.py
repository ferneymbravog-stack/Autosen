"""Migración preparatoria: habilita NULL en Id_vehiculo, crea placa_historica y limpia huérfanos."""
from django.db import migrations, models


def limpiar_huerfanos_y_llenar_placas(apps, schema_editor):
    Vehiculo = apps.get_model("core", "Vehiculo")
    Lectura = apps.get_model("core", "Lectura")
    Alerta = apps.get_model("core", "Alerta")

    placas_por_id = dict(Vehiculo.objects.values_list("id_vehiculo", "placa"))
    ids_existentes = set(placas_por_id.keys())

    lecturas_huerfanas = (
        Lectura.objects.filter(id_vehiculo__isnull=False)
        .exclude(id_vehiculo__in=ids_existentes)
        .update(id_vehiculo=None)
    )
    alertas_huerfanas = (
        Alerta.objects.filter(id_vehiculo__isnull=False)
        .exclude(id_vehiculo__in=ids_existentes)
        .update(id_vehiculo=None)
    )

    for vid, placa in placas_por_id.items():
        if placa:
            Lectura.objects.filter(id_vehiculo=vid, placa_historica__isnull=True).update(placa_historica=placa)
            Alerta.objects.filter(id_vehiculo=vid, placa_historica__isnull=True).update(placa_historica=placa)

    print(
        f"  [0009] Registros huérfanos puestos en NULL -> "
        f"lecturas: {lecturas_huerfanas}, alertas: {alertas_huerfanas}."
    )


def revertir_huerfanos(apps, schema_editor):
    Lectura = apps.get_model("core", "Lectura")
    Alerta = apps.get_model("core", "Alerta")
    Lectura.objects.filter(id_vehiculo__isnull=True).update(id_vehiculo=0)
    Alerta.objects.filter(id_vehiculo__isnull=True).update(id_vehiculo=0)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_renombrar_web_push_a_navegador"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lectura",
            name="id_vehiculo",
            field=models.IntegerField(blank=True, db_column="Id_vehiculo", db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name="alerta",
            name="id_vehiculo",
            field=models.IntegerField(blank=True, db_column="Id_vehiculo", db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="lectura",
            name="placa_historica",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name="alerta",
            name="placa_historica",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.RunPython(limpiar_huerfanos_y_llenar_placas, revertir_huerfanos),
    ]
