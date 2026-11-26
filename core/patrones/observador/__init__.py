"""
GoF – Observer.

alerta_critica es el evento (equivale a AlertaCriticaEvento): se emite cuando se
registra una alerta. atender_alerta_critica es el observador (equivale a
AlertaCriticaListener); se suscribe en CoreConfig.ready().
"""
import logging

from django.dispatch import Signal

from core.utilidades import texto_java

# Argumento enviado: alerta (core.models.Alerta).
alerta_critica = Signal()

LOG = logging.getLogger("autosen.observador")


def atender_alerta_critica(sender, alerta, **kwargs):
    LOG.warning(
        "[OBSERVER] Alerta registrada -> Sensor '%s' (vehículo %s) nivel %s%% | %s",
        texto_java(alerta.nombre_sensor),
        texto_java(alerta.vehiculo_id),
        texto_java(alerta.nivel),
        texto_java(alerta.mensaje),
    )
    # Despacho automático de notificaciones multicanal (Email, WhatsApp, Telegram y Navegador)
    try:
        from django.conf import settings
        from core import notificaciones
        if getattr(settings, "NOTIFICACIONES_ASINCRONAS", False):
            notificaciones.despachar_en_segundo_plano(alerta)
        else:
            notificaciones.despachar_notificacion_multicanal(alerta)
    except Exception as exc:
        LOG.error("[OBSERVER] Error al despachar notificaciones: %s", exc)
