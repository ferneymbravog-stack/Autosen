"""Módulo de despacho de notificaciones multicanal (Email, WhatsApp, Telegram y Navegador)."""
import html
import logging
import threading

from django.conf import settings
from django.db import connection, transaction
from django.template.loader import render_to_string

from core.models import Alerta, Cliente, NotificacionEnviada, Vehiculo
from core.normalizacion import normalizar_telefono_whatsapp
from core.servicios_externos import (
    email_configurado,
    enviar_email,
    enviar_telegram,
    enviar_whatsapp,
    telegram_configurado,
    whatsapp_configurado,
)
from core.utilidades import ahora

LOG = logging.getLogger("autosen.notificaciones")


def _escapar_whatsapp(valor) -> str:
    """Limpia caracteres de formato de WhatsApp en datos dinámicos."""
    texto = str(valor if valor is not None else "")
    for ch in ("*", "_", "~", "`"):
        texto = texto.replace(ch, "")
    return texto


def formatear_mensaje_whatsapp(alerta: Alerta, nombre_cliente: str, nombre_veh: str,
                               placa: str, tipo_str: str) -> str:
    """Construye el mensaje en texto plano para WhatsApp con formato en negrita."""
    return (
        f"🚨 *AutoSen OBD2 Alerta*\n\n"
        f"Hola *{_escapar_whatsapp(nombre_cliente)}*,\n"
        f"Vehículo: *{_escapar_whatsapp(nombre_veh)}* (Placa: *{_escapar_whatsapp(placa)}*)\n"
        f"Sensor: {_escapar_whatsapp(alerta.nombre_sensor)} ({_escapar_whatsapp(alerta.tipo_sensor)})\n"
        f"Nivel: *{alerta.nivel}%*\n"
        f"Estado: *{_escapar_whatsapp(tipo_str)}*\n"
        f"Diagnóstico: {_escapar_whatsapp(alerta.mensaje)}\n\n"
        f"Revisa tu panel de AutoSen."
    )


def formatear_mensaje_telegram(alerta: Alerta, nombre_veh: str, placa: str, propietario: str,
                               telefono: str | None, tipo_str: str) -> str:
    """Construye el mensaje HTML para Telegram escapando todos los datos dinámicos."""
    fecha_str = alerta.fecha_alerta.strftime("%Y-%m-%d %H:%M:%S") if alerta.fecha_alerta else ""
    lineas = [
        "🤖 <b>AutoSen Telemetría Bot</b>",
        f"🔴 <b>{html.escape(str(tipo_str))}</b>",
        f"🚘 <b>Vehículo:</b> {html.escape(str(nombre_veh))} (<i>{html.escape(str(placa))}</i>)",
        f"👤 <b>Propietario:</b> {html.escape(str(propietario))}",
        f"📱 <b>Teléfono:</b> {html.escape(str(telefono or 'No registrado'))}",
        f"📡 <b>Sensor:</b> {html.escape(str(alerta.nombre_sensor))} (<i>{html.escape(str(alerta.tipo_sensor))}</i>)",
        f"📈 <b>Nivel:</b> {html.escape(str(alerta.nivel))}%",
        f"📝 <b>Diagnóstico:</b> {html.escape(str(alerta.mensaje))}",
        f"⏰ <b>Fecha y hora:</b> {html.escape(fecha_str)}",
    ]
    return "\n".join(lineas)[:4000]


def renderizar_html_email_alerta(alerta: Alerta, nombre_veh: str, placa: str,
                                 propietario: str, asunto: str) -> str:
    """Renderiza la plantilla HTML del correo de alerta con autoescape de Django."""
    es_critica = alerta.nivel >= 70
    tipo_str = "FALLA CRÍTICA" if es_critica else "ADVERTENCIA"
    fecha_str = alerta.fecha_alerta.strftime("%Y-%m-%d %H:%M:%S") if alerta.fecha_alerta else ""
    base_url = getattr(settings, "SITE_URL", "http://localhost:8080").rstrip("/")
    return render_to_string(
        "emails/alerta.html",
        {
            "asunto": asunto,
            "es_critica": es_critica,
            "tipo_str": tipo_str,
            "propietario": propietario,
            "vehiculo": nombre_veh,
            "placa": placa,
            "sensor": alerta.nombre_sensor,
            "tipo_sensor": alerta.tipo_sensor,
            "nivel": alerta.nivel,
            "diagnostico": alerta.mensaje,
            "fecha": fecha_str,
            "url_dashboard": f"{base_url}/dashboard",
        },
    )


def despachar_notificacion_multicanal(alerta: Alerta) -> list[NotificacionEnviada]:
    """Despacha la alerta a través de Email, WhatsApp (al número del cliente), Telegram y Navegador."""
    notificaciones = []
    vehiculo = (
        Vehiculo.objects.select_related("cliente").filter(pk=alerta.vehiculo_id).first()
        if alerta.vehiculo_id
        else None
    )
    cliente = vehiculo.cliente if vehiculo else None

    placa = (vehiculo.placa if (vehiculo and vehiculo.placa) else alerta.placa_historica) or (
        f"ID-{alerta.vehiculo_id}" if alerta.vehiculo_id else "SIN-PLACA"
    )
    nombre_veh = vehiculo.nombre_vehiculo if vehiculo else f"Vehículo ({placa})"
    propietario = f"{cliente.nombre_cliente} {cliente.apellido_cliente}" if cliente else "Sin asignar"
    correo_cliente = cliente.correo.strip() if (cliente and cliente.correo and cliente.correo.strip()) else ""

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
        if not correo_cliente:
            estado_em = "OMITIDO"
            error_em = "Cliente sin correo registrado"
            dest_em = "sin correo"
            LOG.info("[NOTIFICACION EMAIL] Omitida: %s.", error_em)
        else:
            dest_em = correo_cliente
            configurado_em = email_configurado()
            html_em = renderizar_html_email_alerta(alerta, nombre_veh, placa, propietario, asunto)
            exito_em, detalle_em = enviar_email(correo_cliente, asunto, cuerpo, html_em)
            if exito_em:
                estado_em = "ENVIADO"
                error_em = None
            elif not configurado_em:
                estado_em = "OMITIDO"
                error_em = detalle_em
            else:
                estado_em = "FALLIDO"
                error_em = detalle_em
        notificaciones.append(
            NotificacionEnviada.objects.create(
                canal="EMAIL",
                destinatario=dest_em,
                asunto=asunto,
                mensaje=cuerpo,
                estado=estado_em,
                detalle_error=error_em,
                alerta=alerta,
            )
        )
    except Exception as exc:
        LOG.error("[NOTIFICACION EMAIL] Error al registrar notificación: %s", exc)

    # 2. Canal WHATSAPP (al número registrado por el cliente)
    try:
        nombre_saludo = cliente.nombre_cliente if cliente else "Cliente"
        mensaje_wa = formatear_mensaje_whatsapp(alerta, nombre_saludo, nombre_veh, placa, tipo_str)
        asunto_wa = f"WhatsApp alerta {placa} ({nombre_saludo})"
        if not telefono_destinatario:
            estado_wa = "OMITIDO"
            error_wa = "Cliente sin teléfono registrado"
            dest_wa = "sin teléfono"
            LOG.info("[NOTIFICACION WHATSAPP] Omitida: El cliente %s no tiene teléfono registrado.", propietario)
        elif not whatsapp_configurado():
            estado_wa = "OMITIDO"
            error_wa = "WhatsApp no configurado"
            dest_wa = normalizar_telefono_whatsapp(telefono_destinatario) or telefono_destinatario
            LOG.info("[NOTIFICACION WHATSAPP] Omitida para %s: WhatsApp no configurado.", dest_wa)
        else:
            numero_norm = normalizar_telefono_whatsapp(telefono_destinatario)
            if not numero_norm:
                estado_wa = "FALLIDO"
                error_wa = "Teléfono inválido"
                dest_wa = telefono_destinatario
            else:
                dest_wa = numero_norm
                exito_wa, detalle_wa = enviar_whatsapp(numero_norm, mensaje_wa)
                estado_wa = "ENVIADO" if exito_wa else "FALLIDO"
                error_wa = None if exito_wa else detalle_wa
        notificaciones.append(
            NotificacionEnviada.objects.create(
                canal="WHATSAPP",
                destinatario=dest_wa,
                asunto=asunto_wa,
                mensaje=mensaje_wa,
                estado=estado_wa,
                detalle_error=error_wa,
                alerta=alerta,
            )
        )
    except Exception as exc:
        LOG.error("[NOTIFICACION WHATSAPP] Error al registrar notificación: %s", exc)

    # 3. Canal TELEGRAM
    try:
        chat_id = getattr(settings, "TELEGRAM_CHAT_ID", "").strip()
        destinatario_tg = chat_id if chat_id else "sin configurar"
        mensaje_tg = formatear_mensaje_telegram(
            alerta, nombre_veh, placa, propietario, telefono_destinatario, tipo_str
        )
        configurado_tg = telegram_configurado()
        exito_tg, detalle_tg = enviar_telegram(mensaje_tg)
        if exito_tg:
            estado_tg = "ENVIADO"
            error_tg = None
        elif not configurado_tg:
            estado_tg = "OMITIDO"
            error_tg = detalle_tg
        else:
            estado_tg = "FALLIDO"
            error_tg = detalle_tg
        notificaciones.append(
            NotificacionEnviada.objects.create(
                canal="TELEGRAM",
                destinatario=destinatario_tg,
                asunto=f"Telegram alerta {placa}",
                mensaje=mensaje_tg,
                estado=estado_tg,
                detalle_error=error_tg,
                alerta=alerta,
            )
        )
    except Exception as exc:
        LOG.error("[NOTIFICACION TELEGRAM] Error al registrar notificación: %s", exc)

    # 4. Canal NAVEGADOR (queda EN_COLA hasta que la API Notification del navegador la muestre)
    try:
        dest_nav = correo_cliente if correo_cliente else "Panel Administrativo"
        notif_nav, _ = NotificacionEnviada.objects.get_or_create(
            alerta=alerta,
            canal="NAVEGADOR",
            defaults={
                "destinatario": dest_nav,
                "asunto": f"AutoSen: {tipo_str}",
                "mensaje": f"Placa {placa} - {alerta.nombre_sensor} {alerta.nivel}%",
                "estado": "EN_COLA",
                "detalle_error": None,
            },
        )
        notificaciones.append(notif_nav)
        LOG.info("[NOTIFICACION NAVEGADOR] En cola para notificación del navegador (%s).", dest_nav)
    except Exception as exc:
        LOG.error("[NOTIFICACION NAVEGADOR] Error: %s", exc)

    return notificaciones


def _lanzar_hilo_despacho(alerta_id: int) -> None:
    """Inicia un hilo demonio para despachar las notificaciones y cierra la conexión BD al finalizar."""

    def _tarea() -> None:
        try:
            alerta_bd = Alerta.objects.filter(pk=alerta_id).first()
            if alerta_bd is not None:
                despachar_notificacion_multicanal(alerta_bd)
        except Exception as exc:
            LOG.error("[NOTIFICACIONES] Error en hilo de segundo plano: %s", exc)
        finally:
            connection.close()

    hilo = threading.Thread(target=_tarea, name=f"autosen-notif-{alerta_id}", daemon=True)
    hilo.start()


def despachar_en_segundo_plano(alerta: Alerta) -> None:
    """Programa el envío multicanal tras confirmar la transacción en base de datos."""
    alerta_id = alerta.pk
    if alerta_id is None:
        return
    transaction.on_commit(lambda: _lanzar_hilo_despacho(alerta_id))


def reintentar_notificacion(notif: NotificacionEnviada) -> tuple[bool, str]:
    """Reintenta el envío de una notificación fallida de Telegram, Email o WhatsApp."""
    if notif.canal not in ("TELEGRAM", "EMAIL", "WHATSAPP"):
        return False, "Este canal no admite reintento manual."

    if notif.canal == "TELEGRAM":
        exito, detalle = enviar_telegram(notif.mensaje)
        chat_id = getattr(settings, "TELEGRAM_CHAT_ID", "").strip()
        if exito and chat_id:
            notif.destinatario = chat_id
    elif notif.canal == "EMAIL":
        alerta = notif.alerta
        if alerta is not None:
            vehiculo = (
                Vehiculo.objects.select_related("cliente").filter(pk=alerta.vehiculo_id).first()
                if alerta.vehiculo_id
                else None
            )
            cliente = vehiculo.cliente if vehiculo else None
            placa = (vehiculo.placa if (vehiculo and vehiculo.placa) else alerta.placa_historica) or (
                f"ID-{alerta.vehiculo_id}" if alerta.vehiculo_id else "SIN-PLACA"
            )
            nombre_veh = vehiculo.nombre_vehiculo if vehiculo else f"Vehículo ({placa})"
            propietario = f"{cliente.nombre_cliente} {cliente.apellido_cliente}" if cliente else "Sin asignar"
            html_cuerpo = renderizar_html_email_alerta(alerta, nombre_veh, placa, propietario, notif.asunto)
        else:
            html_cuerpo = f"<pre style='font-family:sans-serif'>{html.escape(notif.mensaje)}</pre>"
        exito, detalle = enviar_email(notif.destinatario, notif.asunto, notif.mensaje, html_cuerpo)
    else:
        exito, detalle = enviar_whatsapp(notif.destinatario, notif.mensaje)

    notif.estado = "ENVIADO" if exito else "FALLIDO"
    notif.detalle_error = None if exito else detalle
    notif.fecha_envio = ahora()
    notif.save()
    return exito, detalle
