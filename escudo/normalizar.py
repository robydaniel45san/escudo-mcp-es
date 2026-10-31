"""Normalización de texto antes de buscar intenciones.

Deshace los disfraces más comunes en descripciones de herramientas MCP:
caracteres invisibles, letras de otros alfabetos que imitan a las latinas,
tildes y mayúsculas.
"""
import re
import unicodedata

# Caracteres de ancho cero y marcas invisibles.
INVISIBLES = re.compile("[​‌‍⁠﻿­]")

# Homoglifos cirílicos y griegos que se confunden con letras latinas.
CONFUSABLES = {
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x", "і": "i", "ј": "j", "ѕ": "s", "ԁ": "d", "һ": "h", "ӏ": "l",
    "А": "A", "В": "B", "Е": "E", "К": "K", "М": "M", "Н": "H", "О": "O", "Р": "P", "С": "C", "Т": "T", "Х": "X", "І": "I", "Ј": "J", "Ѕ": "S",
    "ο": "o", "α": "a", "ε": "e", "ι": "i", "κ": "k", "ν": "v", "ρ": "p", "τ": "t", "υ": "u", "χ": "x",
    "Α": "A", "Β": "B", "Ε": "E", "Ζ": "Z", "Η": "H", "Ι": "I", "Κ": "K", "Μ": "M", "Ν": "N", "Ο": "O", "Ρ": "P", "Τ": "T", "Υ": "Y", "Χ": "X",
}
_CONF_RE = re.compile("[" + "".join(CONFUSABLES) + "]")


def _es_latina(ch):
    return "LATIN" in unicodedata.name(ch, "")


def _es_imitadora(ch):
    """Solo cuenta la letra no latina que se ve igual a una latina (la "о" cirílica, no la "Ω")."""
    return ch in CONFUSABLES


def palabras_mezcladas(texto):
    """Palabras que combinan letras latinas con cirílicas o griegas, o con invisibles en medio.

    Una palabra rusa o griega completa es legítima; una mezcla dentro de la
    misma palabra es una señal de disfraz.
    """
    sospechosas = []
    for palabra in re.findall(r"[^\s.,;:!?()«»\"'<>/]+", texto):
        letras = [c for c in INVISIBLES.sub("", palabra) if c.isalpha()]
        if not letras:
            continue
        latinas = sum(_es_latina(c) for c in letras)
        imitadoras = sum(_es_imitadora(c) for c in letras)
        invisible_entre_letras = bool(re.search(r"\w[​‌⁠﻿­]\w", palabra))
        if (latinas and imitadoras) or invisible_entre_letras:
            sospechosas.append(palabra)
    return sospechosas


def normalizar(texto):
    """Texto en minúsculas, sin invisibles, sin homoglifos y sin tildes."""
    t = INVISIBLES.sub("", texto)
    t = _CONF_RE.sub(lambda m: CONFUSABLES[m.group(0)], t)
    t = unicodedata.normalize("NFKD", t)
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"\s+", " ", t)
    return t.lower().strip()
