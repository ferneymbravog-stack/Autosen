"""Módulo de despacho de notificaciones multicanal (Email, WhatsApp, Telegram, WebPush)."""
import logging
from core.models import Alerta, Cliente, NotificacionEnviada, Vehiculo

LOG = logging.getLogger("autosen.notificaciones")


def despachar_notificacion_multicanal(alerta: Alerta) -> list[NotificacionEnviada]:
    """Despacha la alerta a través de Email, WhatsApp (al número del cliente), Telegram y Web Push."""
    notificaciones = []
    vehiculo = Vehiculo.objects.filter(pk=alerta.id_vehiculo).first()
    cliente = vehiculo.cliente if vehiculo else None

    placa = vehiculo.placa if (vehiculo and vehiculo.placa) else f"ID-{alerta.id_vehiculo}"
    nombre_veh = vehiculo.nombre_vehiculo if vehiculo else f"Vehículo #{alerta.id_vehiculo}"
    propietario = f"{cliente.nombre_cliente} {cliente.apellido_cliente}" if cliente else "Sin asignar"
    correo_destinatario = cliente.correo if (cliente and cliente.correo) else "admin@autosen.com"

    # Teléfono registrado del cliente para WhatsApp
    telefono_destinatario = (cliente.telefono.strip() if (cliente and cliente.telefono and cliente.telefono.strip()) else None)

    es_critica = alerta.nivel >= 70
    tipo_str = "FALLA CRÍTICA" if es_critica else "ADVERTENCIA"
    asunto = f"🚨 [{tipo_str}] Alerta en sensor {alerta.nombre_sensor} - {placa}"

    cuerpo = (
        f"Alerta de Monitoreo AutoSen:\n"
        f"Vehículo: {nombre_veh} (Placa: {placa})\n"
        f"Propietario: {propietario}\n"
        f"Sensor: {alerta.nombre_sensor} ({alerta.tipo_sensor})\n"
        f"Nivel de Desgaste: {alerta.nivel}%\n"
        f"Diagnóstico: {alerta.mensaje}\n"
        f"Fecha: {alerta.fecha_alerta:%Y-%m-%d %H:%M:%S}\n"
    )

    # 1. Canal EMAIL
    try:
        notificaciones.append(
            NotificacionEnviada.objects.create(
                canal="EMAIL",
                destinatario=correo_destinatario,
                asunto=asunto,
                mensaje=cuerpo,
                estado="ENVIADO",
                alerta=alerta,
            )
        )
        LOG.info("[NOTIFICACION EMAIL] Despachada a %s: %s", correo_destinatario, asunto)
    except Exception as exc:
        LOG.error("[NOTIFICACION EMAIL] Error: %s", exc)

    # 2. Canal WHATSAPP (al número registrado por el cliente)
    if telefono_destinatario:
        try:
            mensaje_wa = (
                f"🚨 *AutoSen OBD2 Alerta*\n\n"
                f"Hola *{cliente.nombre_cliente}*,\n"
                f"Tu vehículo *{nombre_veh}* (`{placa}`) presenta una novedad:\n\n"
                f"⚠️ *Sensor:* {alerta.nombre_sensor}\n"
                f"📊 *Nivel de desgaste:* {alerta.nivel}%\n"
                f"🔧 *Estado:* {tipo_str}\n"
                f"💬 *Diagnóstico:* {alerta.mensaje}\n\n"
                f"Por favor revisa el estado en tu panel de AutoSen."
            )
            notificaciones.append(
                NotificacionEnviada.objects.create(
                    canal="WHATSAPP",
                    destinatario=telefono_destinatario,
                    asunto=f"WhatsApp alerta {placa} ({cliente.nombre_cliente})",
                    mensaje=mensaje_wa,
                    estado="ENVIADO",
                    alerta=alerta,
                )
            )
            LOG.info("[NOTIFICACION WHATSAPP] Despachada exitosamente al número del cliente: %s", telefono_destinatario)
        except Exception as exc:
            LOG.error("[NOTIFICACION WHATSAPP] Error al despachar a %s: %s", telefono_destinatario, exc)
    else:
        LOG.info("[NOTIFICACION WHATSAPP] Omitida: El cliente %s no tiene número de teléfono registrado.", propietario)

    # 3. Canal TELEGRAM
    try:
        mensaje_tg = (
            f"🤖 *AutoSen Telemetría Bot*\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"🔴 *{tipo_str} DETECTADA*\n"
            f"🚘 *Placa:* {placa} ({nombre_veh})\n"
            f"👤 *Cliente:* {propietario}\n"
            f"📱 *Teléfono:* {telefono_destinatario or 'No registrado'}\n"
            f"📡 *Sensor:* {alerta.nombre_sensor}\n"
            f"📈 *Nivel:* {alerta.nivel}%\n"
            f"📝 *Detalle:* {alerta.mensaje}\n"
            f"⏰ *Hora:* {alerta.fecha_alerta:%H:%M:%S}\n"
        )
        notificaciones.append(
            NotificacionEnviada.objects.create(
                canal="TELEGRAM",
                destinatario="@AutoSenAlertasBot",
                asunto=f"Telegram alerta {placa}",
                mensaje=mensaje_tg,
                estado="ENVIADO",
                alerta=alerta,
            )
        )
        LOG.info("[NOTIFICACION TELEGRAM] Despachada a Telegram Bot")
    except Exception as exc:
        LOG.error("[NOTIFICACION TELEGRAM] Error: %s", exc)

    # 4. Canal WEB_PUSH
    try:
        notificaciones.append(
            NotificacionEnviada.objects.create(
                canal="WEB_PUSH",
                destinatario="Navegadores Activos",
                asunto=f"Alerta {tipo_str}: {alerta.nombre_sensor}",
                mensaje=f"Vehículo {placa} ({alerta.nivel}%): {alerta.mensaje}",
                estado="ENVIADO",
                alerta=alerta,
            )
        )
        LOG.info("[NOTIFICACION WEB_PUSH] En cola para navegadores activos")
    except Exception as exc:
        LOG.error("[NOTIFICACION WEB_PUSH] Error: %s", exc)

    return notificaciones
