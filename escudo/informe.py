"""Informe del hallazgo para el analista.

El Escudo decide si la descripción está envenenada. Este módulo no vuelve a
detectar: redacta lo que ya se encontró, cita la frase de cada regla y rechaza
cualquier archivo, URL o IP que no esté en la descripción.

Varias alertas sobre la misma descripción (mcpscan, mcp-audit, Escudo ES)
cuentan como un solo incidente.
"""
import re

from .normalizar import normalizar

# Hechos concretos que un resumen puede inventar. El resto de la frase es
# explicación de la regla, no un dato nuevo.
_IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_URL = re.compile(r"https?://[^\s»\"']+")
_ARCHIVO = re.compile(r"/etc/shadow|/etc/passwd|\.env\b|\.ssh\b|\bid_rsa\b")

# Datos de documentación (TEST-NET, RFC 5737). No salen de ninguna descripción.
_IP_AJENA = "203.0.113.50"
_ARCHIVO_AJENO = "/etc/shadow"

_QUE = {
    "ignorar_instrucciones": "pide ignorar las instrucciones del sistema",
    "instrucciones_anuladas": "dice que las instrucciones del sistema ya no aplican",
    "ocultar_al_usuario": "pide ocultarle algo a la persona que usa el agente",
    "leer_o_enviar_secretos": "pide leer o enviar un secreto",
    "enviar_contrasenas": "pide enviar una contraseña a otro destino",
    "exfiltrar_datos_usuario": "pide sacar datos de la persona usuaria",
    "orden_previa": "da una orden para ejecutar antes de usar la herramienta",
    "etiqueta_de_sistema": "imita una etiqueta de instrucción del sistema",
    "texto_disfrazado": "mezcla letras de otro alfabeto para disfrazar una palabra",
}


def _cita_presente(frase, texto_normalizado):
    if not frase:
        return False
    cita = normalizar(frase)
    if cita in texto_normalizado:
        return True
    partes = [p for p in cita.split() if p]
    return bool(partes) and all(p in texto_normalizado for p in partes)


def inventados(texto, texto_normalizado):
    """Archivos, URLs e IPs del texto que no aparecen en la descripción."""
    vistos = []
    for patron in (_IP, _URL, _ARCHIVO):
        for hallazgo in patron.findall(normalizar(texto)):
            if hallazgo not in texto_normalizado and hallazgo not in vistos:
                vistos.append(hallazgo)
    return vistos


def _afirmacion(regla, frase, texto_normalizado):
    que = _QUE.get(regla, "activó una regla del Escudo")
    texto = f"La descripción {que}: «{frase}»."
    ajenos = inventados(texto, texto_normalizado)
    return {
        "regla": regla,
        "cita": frase,
        "texto": texto,
        "cita_valida": _cita_presente(frase, texto_normalizado),
        "inventados": ajenos,
        "respaldada": _cita_presente(frase, texto_normalizado) and not ajenos,
    }


def resumen_sin_citas(hallazgos, texto_normalizado):
    """Línea base: el mismo caso, dicho sin citar y con dos datos que no están.

    No es la salida de un modelo. Es la plantilla contra la que se mide el
    verificador: agrega siempre una IP y un archivo de documentación.
    """
    if not hallazgos:
        return {"texto": "", "inventados": [], "rechazado": False}
    texto = (
        "Hubo un intento de tool poisoning. "
        f"Se copió {_ARCHIVO_AJENO} y se envió a {_IP_AJENA}."
    )
    ajenos = inventados(texto, texto_normalizado)
    return {"texto": texto, "inventados": ajenos, "rechazado": bool(ajenos)}


def _fuentes(mcpscan, mcpaudit, escudo):
    fuentes = []
    if mcpscan and not mcpscan.get("error") and mcpscan.get("envenenada"):
        fuentes.append("mcpscan")
    if mcpaudit and not mcpaudit.get("error") and mcpaudit.get("envenenada"):
        fuentes.append("mcp-audit")
    if escudo and escudo.get("envenenada"):
        fuentes.append("Escudo ES")
    return fuentes


def _incidente(fuentes):
    n = len(fuentes)
    if n == 0:
        return {
            "hay": False,
            "alertas": 0,
            "fuentes": [],
            "texto": "Ningún detector marcó esta descripción. No hay incidente que informar.",
        }
    if n == 1:
        return {
            "hay": True,
            "alertas": 1,
            "fuentes": fuentes,
            "texto": f"1 alerta ({fuentes[0]}): 1 incidente.",
        }
    lista = ", ".join(fuentes)
    return {
        "hay": True,
        "alertas": n,
        "fuentes": fuentes,
        "texto": f"{n} alertas ({lista}) son 1 incidente: la misma descripción.",
    }


def redactar(descripcion, escudo, mcpscan=None, mcpaudit=None):
    """Informe fiel a la descripción, más la comparación con el resumen sin citas.

    `escudo` es el dict que devuelve `escudo.analizar`.
    """
    texto = normalizar(descripcion or "")
    hallazgos = (escudo or {}).get("hallazgos") or []
    afirmaciones = [_afirmacion(h["regla"], h["frase"], texto) for h in hallazgos]
    respaldadas = sum(1 for a in afirmaciones if a["respaldada"])
    return {
        "incidente": _incidente(_fuentes(mcpscan, mcpaudit, escudo)),
        "afirmaciones": afirmaciones,
        "respaldadas": respaldadas,
        "total": len(afirmaciones),
        "sin_citas": resumen_sin_citas(hallazgos, texto),
    }
