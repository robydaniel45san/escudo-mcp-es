"""Detección de secretos en los argumentos que un agente envía a una herramienta (capa 4 del escudo).

Busca el canario del laboratorio, asignaciones típicas de claves y formatos conocidos
de tokens y llaves privadas. Solo biblioteca estándar: lo usan el verificador y la web.
"""
import re

SECRETO = re.compile(r"CANARIO-[A-Z0-9-]+|(api[_-]?key|password|secret|token|contrasena)\s*[=:]\s*\S+|"
                     r"sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----", re.I)


def buscar_secreto(texto):
    """Devuelve la parte que parece un secreto, recortada para no repetirla entera, o None."""
    m = SECRETO.search(texto or "")
    return (m.group(0)[:24] + "…") if m else None
