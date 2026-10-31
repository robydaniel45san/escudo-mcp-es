"""Escudo ES: detector bilingüe de instrucciones escondidas en descripciones de herramientas MCP."""
from .normalizar import normalizar, palabras_mezcladas
from .reglas import buscar


def analizar(descripcion):
    """Analiza una descripción y devuelve un veredicto explicable.

    Devuelve un dict con:
      envenenada: bool
      hallazgos: lista de {regla, frase}
      disfraz: palabras con alfabetos mezclados o caracteres invisibles
      normalizado: el texto que analizan las reglas
    """
    normalizado = normalizar(descripcion)
    hallazgos = [{"regla": r, "frase": f} for r, f in buscar(normalizado)]
    disfraz = palabras_mezcladas(descripcion)
    if disfraz:
        hallazgos.append({"regla": "texto_disfrazado", "frase": " ".join(disfraz[:3])})
    return {
        "envenenada": bool(hallazgos),
        "hallazgos": hallazgos,
        "disfraz": disfraz,
        "normalizado": normalizado,
    }
