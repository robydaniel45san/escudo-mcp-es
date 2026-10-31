"""Reglas bilingües de intención (inglés, español y spanglish).

Las reglas buscan intenciones, no frases exactas. Se aplican sobre el texto ya
normalizado (minúsculas, sin tildes ni homoglifos). Se escribieron mirando solo
dataset/casos_desarrollo.jsonl.
"""
import re

# Verbos de acción sobre datos, en los dos idiomas (imperativo y conjugaciones frecuentes).
_VERBO_DATO = (r"(read|send|sends|upload|include|attach|copy|pass|forward|post|share|exfiltrate|"
               r"lee|leer|leelo|envia|enviar|envialo|manda|mandar|mandalo|sube|subir|subelo|incluye|incluir|"
               r"adjunta|adjuntar|copia|copiar|reenvia|pasa|pasar|comparte)")
_SECRETO_FUERTE = (r"(\.env\b|id_rsa|\.ssh|api[ _-]?keys?|credentials?|credenciales|secrets?\b|secretos|"
                   r"tokens?\b|private key|clave privada|claves\b|keys\b)")
_SECRETO_DEBIL = r"(passwords?|contrasenas?|claves? de acceso)"
_DESTINO = (r"(field|parameter|param|notes|metadata|body|endpoint|request|server|backup|url|"
            r"campo|parametro|notas|metadatos|cuerpo|peticion|servidor|respaldo)")
_DATOS_USUARIO = (r"(chat history|conversation|user'?s files|files del usuario|archivos del usuario|"
                  r"historial|conversacion)")

REGLAS = [
    # Ignorar o reemplazar las instrucciones del sistema.
    ("ignorar_instrucciones", re.compile(
        r"\b(ignore|ignora|ignorar|disregard|forget|olvida|olvidar|omite|descarta|override|haz caso omiso)\b"
        r".{0,40}\b(instructions?|instrucciones|indicaciones|rules|reglas|guidance|guidelines|directions|directrices)\b")),
    ("instrucciones_anuladas", re.compile(
        r"\b(instructions?|instrucciones|rules|reglas|indicaciones|guidance)\b.{0,30}"
        r"\b(no longer apply|don'?t apply|do not apply|ya no aplican|no aplican|quedan sin efecto)\b")),
    # Ocultarle algo a la persona usuaria.
    ("ocultar_al_usuario", re.compile(
        r"\b(do not|don'?t|never|no|nunca)\b(\s+(le|se lo|lo|les))?\s+"
        r"(tell|mention|reveal|inform|disclose|digas|menciones|avises|informes|reveles|reveal|cuentes|muestres)"
        r"|\b(keep|manten|mantener|guarda)\b.{0,30}\b(secret|secreto|hidden|oculto|oculta|confidential|confidencial)\b"
        r"|\ben secreto\b|\bsin que (el usuario|la persona|lo sepa|se entere)"
        r"|\b(silently|quietly|en silencio|a escondidas|sin avisar)\b")),
    # Leer o enviar secretos a un destino.
    ("leer_o_enviar_secretos", re.compile(
        _VERBO_DATO + r"\b.{0,60}" + _SECRETO_FUERTE + r"|" + _SECRETO_FUERTE + r".{0,40}\b" + _VERBO_DATO + r"\b")),
    ("enviar_contrasenas", re.compile(
        _VERBO_DATO + r"\b.{0,40}" + _SECRETO_DEBIL + r".{0,40}\b" + _DESTINO + r"\b")),
    # Sacar datos de la persona usuaria hacia otro lugar.
    ("exfiltrar_datos_usuario", re.compile(
        _VERBO_DATO + r"\b.{0,40}\b" + _DATOS_USUARIO + r"\b.{0,40}\b(to|al|a|en|hacia|into)\b")),
    # Órdenes que la herramienta da al agente antes de usarla.
    ("orden_previa", re.compile(
        r"\b(before using (this|the) tool|before usar|antes de usar (esta herramienta|la herramienta|this tool)|"
        r"prior to (any|each|every) (call|use)|previo a (cualquier|cada) (llamada|call|uso)|"
        r"always (start|begin) by|siempre (empieza|comienza|empezar)|you must (first|always)|debes (primero|siempre))")),
    # Etiquetas que imitan instrucciones del sistema.
    ("etiqueta_de_sistema", re.compile(r"<\s*/?\s*(important|system|instructions?|importante)\s*>|nota para el asistente|note to the assistant")),
]


def buscar(texto_normalizado):
    """Lista de (regla, frase) que se activan en el texto normalizado."""
    hallazgos = []
    for nombre, patron in REGLAS:
        m = patron.search(texto_normalizado)
        if m:
            hallazgos.append((nombre, m.group(0)))
    return hallazgos
