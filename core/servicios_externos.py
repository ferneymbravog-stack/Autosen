"""Clientes de integración con servicios externos (Telegram, Gmail SMTP y WhatsApp Cloud API)."""
import json
import logging
import smtplib
import socket
import urllib.error
import urllib.request

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from core.normalizacion import normalizar_telefono_whatsapp

LOG = logging.getLogger("autosen.externos")
TIMEOUT_HTTP = 5
MAX_CARACTERES_TELEGRAM = 4000


def _ocultar_secretos(texto: str, *secretos: str) -> str:
    """Elimina cualquier aparición accidental de tokens o contraseñas en un mensaje."""
    limpio = str(texto or "")
    for secreto in secretos:
        if secreto:
            limpio = limpio.replace(secreto, "[OCULTO]")
    return limpio


def telegram_configurado() -> bool:
    """Indica si existen credenciales configuradas para Telegram Bot API."""
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = getattr(settings, "TELEGRAM_CHAT_ID", "").strip()
    return bool(token and chat_id)


def email_configurado() -> bool:
    """Indica si existen credenciales SMTP configuradas para el envío de correos."""
    usuario = getattr(settings, "EMAIL_HOST_USER", "").strip()
    clave = getattr(settings, "EMAIL_HOST_PASSWORD", "").strip()
    return bool(usuario and clave)


def whatsapp_configurado() -> bool:
    """Indica si existen las variables requeridas para WhatsApp Cloud API de Meta."""
    token = getattr(settings, "WHATSAPP_TOKEN", "").strip()
    phone_id = getattr(settings, "WHATSAPP_PHONE_NUMBER_ID", "").strip()
    version = getattr(settings, "WHATSAPP_API_VERSION", "").strip()
    return bool(token and phone_id and version)


def _traducir_error_meta(http_status: int | None, codigo, mensaje_meta: str, token: str) -> str:
    """Traduce códigos frecuentes de WhatsApp Cloud API al español conservando código y mensaje."""
    mensaje_limpio = _ocultar_secretos(mensaje_meta, token).strip()
    sufijo = f" (código {codigo}: {mensaje_limpio})" if (codigo and mensaje_limpio) else (
        f" ({mensaje_limpio})" if mensaje_limpio else ""
    )
    if http_status == 401 or codigo == 190:
        return f"Token de WhatsApp inválido o vencido.{sufijo}"
    if codigo == 131047:
        return (
            "El destinatario no ha escrito al número en las últimas 24 horas "
            "(regla de WhatsApp). Pídele que envíe un mensaje al número de prueba."
            f"{sufijo}"
        )
    if codigo == 131030:
        return f"El número no está en la lista de destinatarios permitidos del número de prueba de Meta.{sufijo}"
    if codigo is not None:
        return f"Error de WhatsApp Cloud API (código {codigo}): {mensaje_limpio or 'sin detalle'}"
    if http_status is not None:
        return f"Error HTTP {http_status} en WhatsApp Cloud API{': ' + mensaje_limpio if mensaje_limpio else ''}"
    return mensaje_limpio or "Error desconocido en WhatsApp Cloud API"


def enviar_whatsapp(numero: str, texto: str) -> tuple[bool, str]:
    """Envía un mensaje de texto mediante WhatsApp Cloud API de Meta y devuelve (éxito, detalle)."""
    if not (numero or "").strip():
        LOG.info("[WHATSAPP] Envío omitido: destinatario sin teléfono.")
        return False, "Cliente sin teléfono registrado"

    numero_norm = normalizar_telefono_whatsapp(numero)
    if not numero_norm:
        LOG.warning("[WHATSAPP] Envío fallido: Teléfono inválido (%s).", numero)
        return False, "Teléfono inválido"

    token = getattr(settings, "WHATSAPP_TOKEN", "").strip()
    phone_id = getattr(settings, "WHATSAPP_PHONE_NUMBER_ID", "").strip()
    version = getattr(settings, "WHATSAPP_API_VERSION", "").strip().strip("/")
    if not token or not phone_id or not version:
        LOG.info("[WHATSAPP] Envío omitido a %s: WhatsApp no configurado.", numero_norm)
        return False, "WhatsApp no configurado"

    url = f"https://graph.facebook.com/{version}/{phone_id}/messages"
    carga = json.dumps(
        {
            "messaging_product": "whatsapp",
            "to": numero_norm,
            "type": "text",
            "text": {"preview_url": False, "body": texto or ""},
        }
    ).encode("utf-8")
    peticion = urllib.request.Request(
        url,
        data=carga,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(peticion, timeout=TIMEOUT_HTTP) as respuesta:
            cuerpo_raw = respuesta.read().decode("utf-8")
        datos = json.loads(cuerpo_raw)
        if isinstance(datos, dict) and "error" in datos and isinstance(datos["error"], dict):
            err = datos["error"]
            detalle = _traducir_error_meta(None, err.get("code"), str(err.get("message") or ""), token)
            LOG.error("[WHATSAPP] Error reportado por Meta para %s: %s", numero_norm, detalle)
            return False, detalle
        if isinstance(datos, dict) and datos.get("messages"):
            LOG.info("[WHATSAPP] Mensaje enviado correctamente a %s.", numero_norm)
            return True, "Mensaje enviado por WhatsApp"
        detalle = "Respuesta de WhatsApp sin confirmación de envío"
        LOG.warning("[WHATSAPP] %s (%s)", detalle, numero_norm)
        return False, detalle
    except urllib.error.HTTPError as exc:
        codigo = None
        mensaje_meta = ""
        try:
            cuerpo_err = exc.read().decode("utf-8", errors="replace")
            datos_err = json.loads(cuerpo_err)
            if isinstance(datos_err, dict) and isinstance(datos_err.get("error"), dict):
                codigo = datos_err["error"].get("code")
                mensaje_meta = str(datos_err["error"].get("message") or "")
        except Exception:
            pass
        detalle = _traducir_error_meta(exc.code, codigo, mensaje_meta, token)
        LOG.error("[WHATSAPP] Error HTTP al enviar a %s: %s", numero_norm, detalle)
        return False, detalle
    except (TimeoutError, socket.timeout):
        detalle = "Tiempo de espera agotado al conectar con WhatsApp Cloud API (5 s)"
        LOG.error("[WHATSAPP] %s", detalle)
        return False, detalle
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, (TimeoutError, socket.timeout)):
            detalle = "Tiempo de espera agotado al conectar con WhatsApp Cloud API (5 s)"
        else:
            motivo = _ocultar_secretos(str(exc.reason), token)
            detalle = f"Error de conexión con WhatsApp: {motivo}"
        LOG.error("[WHATSAPP] %s", detalle)
        return False, detalle
    except (json.JSONDecodeError, ValueError):
        detalle = "Respuesta JSON inválida de WhatsApp Cloud API"
        LOG.error("[WHATSAPP] %s", detalle)
        return False, detalle
    except Exception as exc:
        detalle = _ocultar_secretos(f"Error inesperado en WhatsApp: {type(exc).__name__}", token)
        LOG.error("[WHATSAPP] %s", detalle)
        return False, detalle


def enviar_email(destinatario: str, asunto: str, texto: str, html_cuerpo: str) -> tuple[bool, str]:
    """Envía un correo electrónico en texto plano y HTML usando EmailMultiAlternatives."""
    destino = (destinatario or "").strip()
    if not destino:
        LOG.info("[EMAIL] Envío omitido: destinatario sin correo.")
        return False, "Cliente sin correo registrado"

    usuario = getattr(settings, "EMAIL_HOST_USER", "").strip()
    clave = getattr(settings, "EMAIL_HOST_PASSWORD", "").strip()
    if not usuario or not clave:
        LOG.info("[EMAIL] Envío omitido a %s: Email no configurado.", destino)
        return False, "Email no configurado"

    remitente = getattr(settings, "DEFAULT_FROM_EMAIL", "").strip() or usuario
    try:
        mensaje = EmailMultiAlternatives(
            subject=asunto,
            body=texto,
            from_email=remitente,
            to=[destino],
        )
        if html_cuerpo:
            mensaje.attach_alternative(html_cuerpo, "text/html")
        mensaje.send(fail_silently=False)
        LOG.info("[EMAIL] Correo enviado correctamente a %s.", destino)
        return True, "Correo enviado correctamente"
    except smtplib.SMTPException as exc:
        detalle = _ocultar_secretos(f"Error SMTP: {exc}", clave, usuario)
        LOG.error("[EMAIL] Fallo SMTP al enviar a %s: %s", destino, detalle)
        return False, detalle
    except (socket.timeout, TimeoutError):
        detalle = "Tiempo de espera agotado al conectar con el servidor SMTP"
        LOG.error("[EMAIL] %s (destinatario %s)", detalle, destino)
        return False, detalle
    except OSError as exc:
        detalle = _ocultar_secretos(f"Error de red SMTP: {exc}", clave)
        LOG.error("[EMAIL] Fallo de red al enviar a %s: %s", destino, detalle)
        return False, detalle
    except Exception as exc:
        detalle = _ocultar_secretos(f"Error inesperado al enviar correo: {type(exc).__name__}", clave)
        LOG.error("[EMAIL] %s", detalle)
        return False, detalle


def enviar_telegram(texto: str) -> tuple[bool, str]:
    """Envía un mensaje HTML mediante Telegram Bot API y devuelve (éxito, detalle)."""
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = getattr(settings, "TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        LOG.info("[TELEGRAM] Envío omitido: Telegram no configurado.")
        return False, "Telegram no configurado"

    texto_recortado = (texto or "")[:MAX_CARACTERES_TELEGRAM]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    carga = json.dumps(
        {
            "chat_id": chat_id,
            "text": texto_recortado,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
    ).encode("utf-8")
    peticion = urllib.request.Request(
        url,
        data=carga,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(peticion, timeout=TIMEOUT_HTTP) as respuesta:
            cuerpo_raw = respuesta.read().decode("utf-8")
        datos = json.loads(cuerpo_raw)
        if isinstance(datos, dict) and datos.get("ok") is True:
            LOG.info("[TELEGRAM] Mensaje enviado correctamente al chat %s.", chat_id)
            return True, "Mensaje enviado a Telegram"
        descripcion = ""
        if isinstance(datos, dict):
            descripcion = str(datos.get("description") or "")
        detalle = _ocultar_secretos(descripcion or "Telegram respondió ok=false", token)
        LOG.warning("[TELEGRAM] Respuesta no exitosa: %s", detalle)
        return False, detalle
    except urllib.error.HTTPError as exc:
        descripcion = f"HTTP {exc.code}"
        try:
            cuerpo_err = exc.read().decode("utf-8", errors="replace")
            datos_err = json.loads(cuerpo_err)
            if isinstance(datos_err, dict) and datos_err.get("description"):
                descripcion = f"HTTP {exc.code}: {datos_err['description']}"
        except Exception:
            pass
        detalle = _ocultar_secretos(descripcion, token)
        LOG.error("[TELEGRAM] Error HTTP al enviar mensaje: %s", detalle)
        return False, detalle
    except (TimeoutError, socket.timeout):
        detalle = "Tiempo de espera agotado al conectar con Telegram (5 s)"
        LOG.error("[TELEGRAM] %s", detalle)
        return False, detalle
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, (TimeoutError, socket.timeout)):
            detalle = "Tiempo de espera agotado al conectar con Telegram (5 s)"
        else:
            motivo = _ocultar_secretos(str(exc.reason), token)
            detalle = f"Error de conexión con Telegram: {motivo}"
        LOG.error("[TELEGRAM] %s", detalle)
        return False, detalle
    except (json.JSONDecodeError, ValueError):
        detalle = "Respuesta JSON inválida de Telegram"
        LOG.error("[TELEGRAM] %s", detalle)
        return False, detalle
    except Exception as exc:
        detalle = _ocultar_secretos(f"Error inesperado en Telegram: {type(exc).__name__}", token)
        LOG.error("[TELEGRAM] %s", detalle)
        return False, detalle
