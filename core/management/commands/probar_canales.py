"""Comando de consola para verificar la integración con Telegram, Gmail SMTP y WhatsApp Cloud API."""
import html

from django.conf import settings
from django.core.management.base import BaseCommand

from core.servicios_externos import (
    email_configurado,
    enviar_email,
    enviar_telegram,
    enviar_whatsapp,
    telegram_configurado,
    whatsapp_configurado,
)
from core.utilidades import ahora


class Command(BaseCommand):
    help = "Prueba el envío real de notificaciones en cada canal externo configurado."

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            dest="email",
            default="",
            help="Correo electrónico de destino para la prueba SMTP (por defecto EMAIL_HOST_USER).",
        )
        parser.add_argument(
            "--whatsapp",
            dest="whatsapp",
            default="",
            help="Número de teléfono para probar WhatsApp Cloud API (ej. 3001234567).",
        )

    def handle(self, *args, **options):
        marca = ahora().strftime("%Y-%m-%d %H:%M:%S")
        mensaje = f"✅ Prueba de conexión AutoSen ({marca})"
        filas: list[tuple[str, str, str]] = []

        # 1. Telegram
        if not telegram_configurado():
            filas.append(("TELEGRAM", "OMITIDO", "Telegram no configurado"))
        else:
            ok, detalle = enviar_telegram(f"<b>{html.escape(mensaje)}</b>")
            filas.append(("TELEGRAM", "ENVIADO" if ok else "FALLIDO", detalle))

        # 2. Email
        if not email_configurado():
            filas.append(("EMAIL", "OMITIDO", "Email no configurado"))
        else:
            destino_email = (options.get("email") or "").strip() or getattr(settings, "EMAIL_HOST_USER", "").strip()
            html_cuerpo = f"<p><strong>{html.escape(mensaje)}</strong></p>"
            ok, detalle = enviar_email(destino_email, "✅ Prueba de conexión AutoSen", mensaje, html_cuerpo)
            filas.append(("EMAIL", "ENVIADO" if ok else "FALLIDO", f"{destino_email} -> {detalle}"))

        # 3. WhatsApp
        numero_wa = (options.get("whatsapp") or "").strip()
        if not whatsapp_configurado():
            filas.append(("WHATSAPP", "OMITIDO", "WhatsApp no configurado"))
        elif not numero_wa:
            filas.append(("WHATSAPP", "OMITIDO", "Indica --whatsapp NUMERO para enviar mensaje de prueba"))
        else:
            ok, detalle = enviar_whatsapp(numero_wa, mensaje)
            filas.append(("WHATSAPP", "ENVIADO" if ok else "FALLIDO", detalle))

        ancho_canal = max(len("CANAL"), *(len(f[0]) for f in filas))
        ancho_res = max(len("RESULTADO"), *(len(f[1]) for f in filas))
        ancho_det = max(len("DETALLE"), *(len(f[2]) for f in filas))
        linea = f"+-{'-' * ancho_canal}-+-{'-' * ancho_res}-+-{'-' * ancho_det}-+"

        self.stdout.write(linea)
        self.stdout.write(
            f"| {'CANAL'.ljust(ancho_canal)} | {'RESULTADO'.ljust(ancho_res)} | {'DETALLE'.ljust(ancho_det)} |"
        )
        self.stdout.write(linea)
        for canal, resultado, detalle in filas:
            self.stdout.write(
                f"| {canal.ljust(ancho_canal)} | {resultado.ljust(ancho_res)} | {detalle.ljust(ancho_det)} |"
            )
        self.stdout.write(linea)
