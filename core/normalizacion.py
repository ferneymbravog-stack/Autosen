"""
Normalización de datos de vehículos: placa, tipo de placa y modelo (año).

La usan la migración de datos, el importador y las validaciones, para que lo
guardado sea siempre igual venga de la web, del panel, de la API o de un dump.
"""
import re
import unicodedata

TIPOS_PLACA = ("particular", "publico", "oficial", "diplomatico")


def sin_tildes(texto: str | None) -> str:
    """Minúsculas y sin marcas diacríticas: "Público" y "publico" quedan iguales."""
    descompuesto = unicodedata.normalize("NFKD", "" if texto is None else texto)
    return "".join(c for c in descompuesto if not unicodedata.combining(c)).lower()


def normalizar_placa(placa: str | None) -> str | None:
    """Sin espacios alrededor, en mayúsculas y sin el guion de la forma ABC-123: "abc-123" se guarda "ABC123"."""
    if placa is None:
        return None
    placa = placa.strip().upper()
    return placa.replace("-", "") if re.fullmatch(r"[A-Z]{3}-[0-9]{3}", placa) else placa


def normalizar_tipo_placa(tipo: str | None) -> str | None:
    """Uno de TIPOS_PLACA sin importar mayúsculas, tildes ni espacios; None si no es ninguno."""
    if tipo is None:
        return None
    canonico = sin_tildes(tipo.strip())
    return canonico if canonico in TIPOS_PLACA else None


def normalizar_modelo(modelo: str | None) -> str | None:
    """Un año "2020" se guarda como "2020-01-01"; cualquier otro valor se deja igual."""
    if modelo is not None and re.fullmatch(r"\d{4}", modelo):
        return f"{modelo}-01-01"
    return modelo


def normalizar_telefono_whatsapp(telefono: str | None) -> str | None:
    """Normaliza un teléfono al formato internacional de dígitos sin '+' (antepone 57 a celulares CO de 10 dígitos)."""
    if telefono is None:
        return None
    limpio = telefono.strip()
    if not limpio or not re.fullmatch(r"\+?[\d\s\-()]+", limpio):
        return None
    digitos = re.sub(r"[\s\-()+]", "", limpio)
    if not digitos.isdigit():
        return None
    if len(digitos) == 10 and digitos.startswith("3"):
        digitos = "57" + digitos
    if digitos.startswith("0") or not (11 <= len(digitos) <= 15):
        return None
    if digitos.startswith("57") and not re.fullmatch(r"573\d{9}", digitos):
        return None
    return digitos
