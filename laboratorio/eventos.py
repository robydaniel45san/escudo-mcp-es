"""Registro estandarizado del laboratorio: un solo archivo, un solo formato, una sesión por prueba.

Cada evento es una línea JSON en laboratorio/logs/eventos.jsonl con campos tomados de dos estándares:

  OpenTelemetry · convenciones para MCP (estado: Development)
    span.name               "{mcp.method.name} {herramienta}", por ejemplo "tools/call calcular_iva"
    mcp.method.name         tools/list, tools/call, initialize…
    gen_ai.tool.name        nombre de la herramienta
    gen_ai.operation.name   "execute_tool" en las llamadas a herramientas
    trace_id                igual para todos los eventos de una sesión
  OCSF · Detection Finding
    severity_id / severity  0 Unknown · 1 Informational · 2 Low · 3 Medium · 4 High · 5 Critical · 6 Fatal
    action                  Allowed / Denied
    disposition             Allowed / Blocked / Quarantined / Exfiltrated

Como recomienda OpenTelemetry, los argumentos de las llamadas no se guardan completos:
solo una vista recortada y si contienen el canario.

Solo biblioteca estándar: lo usan el atacante, el escudo, el agente simulado y la web.
"""
import datetime as dt
import json
import secrets
from pathlib import Path

LOGS = Path(__file__).resolve().parent / "logs"
EVENTOS = LOGS / "eventos.jsonl"
SESION = LOGS / "sesion.json"
SEVERIDAD = {0: "Unknown", 1: "Informational", 2: "Low", 3: "Medium", 4: "High", 5: "Critical", 6: "Fatal"}


def nueva_sesion(nombre):
    """Empieza una sesión: todos los eventos siguientes llevan su nombre y su trace_id."""
    LOGS.mkdir(exist_ok=True)
    datos = {"sesion": nombre, "trace_id": secrets.token_hex(16), "inicio": ahora()}
    SESION.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
    return datos


def sesion_actual():
    try:
        return json.loads(SESION.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"sesion": "sin-sesion", "trace_id": "0" * 32}


def ahora():
    return dt.datetime.now().astimezone().isoformat(timespec="milliseconds")


def vista_argumentos(argumentos):
    """Vista segura de los argumentos: recortada y con la marca del canario."""
    texto = json.dumps(argumentos or {}, ensure_ascii=False)
    return {"vista": texto[:120] + ("…" if len(texto) > 120 else ""), "contiene_canario": "CANARIO-ARQUISOFT" in texto}


def registrar(componente, evento, mensaje, *, metodo=None, herramienta=None, severidad=1,
              accion=None, disposicion=None, argumentos=None, detalle=None):
    s = sesion_actual()
    registro = {
        "@timestamp": ahora(),
        "sesion": s["sesion"],
        "trace_id": s["trace_id"],
        "span_id": secrets.token_hex(8),
        "componente": componente,
        "evento": evento,
        "span.name": " ".join(x for x in (metodo, herramienta) if x) or evento,
        "mcp.method.name": metodo,
        "gen_ai.tool.name": herramienta,
        "gen_ai.operation.name": "execute_tool" if metodo == "tools/call" else None,
        "severity_id": severidad,
        "severity": SEVERIDAD[severidad],
        "action": accion,
        "disposition": disposicion,
        "mensaje": mensaje,
    }
    if argumentos is not None:
        registro["gen_ai.tool.call.arguments"] = vista_argumentos(argumentos)
    if detalle:
        registro["detalle"] = detalle
    registro = {k: v for k, v in registro.items() if v is not None}
    LOGS.mkdir(exist_ok=True)
    with EVENTOS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")
    return registro


def leer(sesion=None):
    if not EVENTOS.exists():
        return []
    eventos = [json.loads(l) for l in EVENTOS.read_text(encoding="utf-8").splitlines() if l.strip()]
    return [e for e in eventos if sesion is None or e.get("sesion") == sesion]


def puntos_clave(eventos):
    """El quiebre es el primer evento crítico. La defensa es el primer bloqueo del escudo, salvo que
    haya frenado un ataque más específico: un rug pull o una respuesta envenenada definen la sesión."""
    quiebre = next((e for e in eventos if e.get("severity_id", 0) >= 5), None)
    bloqueos = [e for e in eventos if e.get("componente") == "escudo" and e.get("action") == "Denied"]
    defensa = next((e for e in bloqueos if e.get("evento") == "escudo.rug_pull"), None) \
        or next((e for e in bloqueos if e.get("evento") == "escudo.salida_bloqueada"), None) \
        or (bloqueos[0] if bloqueos else None)
    return quiebre, defensa
