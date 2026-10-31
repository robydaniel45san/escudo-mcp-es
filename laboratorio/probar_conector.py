"""Prueba un conector MCP por HTTP: se conecta, pide sus herramientas y las pasa por el Escudo ES.

Solo LEE las descripciones (initialize + tools/list): no llama a ninguna herramienta.
Cada prueba queda en el registro estandarizado como una sesión "Conector-…".

Uso (con el Python de .venv-scanners):
  python laboratorio/probar_conector.py http://127.0.0.1:9100/mcp
  python laboratorio/probar_conector.py http://127.0.0.1:9100/mcp --json
"""
import asyncio
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
sys.path.insert(0, str(AQUI))
from escudo import analizar  # noqa: E402
import eventos  # noqa: E402
from verificador import textos_del_esquema  # noqa: E402


async def leer(url):
    async with streamablehttp_client(url) as (r, w, _):
        async with ClientSession(r, w) as s:
            info = await s.initialize()
            lista = await s.list_tools()
            return info.serverInfo.name, info.serverInfo.version, lista.tools


def probar(url):
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.netloc:
        raise ValueError("La URL tiene que empezar con http:// o https://, por ejemplo http://127.0.0.1:9100/mcp")
    eventos.nueva_sesion(f"Conector-{dt.datetime.now():%H%M%S}")
    eventos.registrar("escudo", "escudo.prueba_conector", f"Prueba de conector: {url}", metodo="initialize")
    try:
        nombre, version, herramientas = asyncio.run(asyncio.wait_for(leer(url), timeout=20))
    except Exception as e:
        eventos.registrar("escudo", "escudo.conector_inaccesible", f"No se pudo conectar a {url}", severidad=2, detalle={"error": str(e)[:200]})
        raise RuntimeError(f"No se pudo conectar a {url}. Revisa que el conector esté corriendo y que hable MCP por HTTP.") from None
    eventos.registrar("escudo", "escudo.lista", f"«{nombre}» respondió con {len(herramientas)} herramientas", metodo="tools/list",
                      detalle={"herramientas": [t.name for t in herramientas]})
    informe = []
    for t in herramientas:
        # Se revisa la descripción y el esquema completo de parámetros (Full-Schema Poisoning).
        res, donde = analizar(t.description or ""), "descripción"
        if not res["envenenada"]:
            for lugar, texto in textos_del_esquema(t.inputSchema or {}):
                r = analizar(texto)
                if r["envenenada"]:
                    res, donde = r, lugar
                    break
        definicion = json.dumps({"descripcion": t.description or "", "esquema": t.inputSchema or {}}, sort_keys=True, ensure_ascii=False)
        item = {"herramienta": t.name, "descripcion": t.description or "", "huella": hashlib.sha256(definicion.encode()).hexdigest()[:16],
                "envenenada": res["envenenada"], "hallazgos": res["hallazgos"], "normalizado": res["normalizado"], "ubicacion": donde}
        informe.append(item)
        if res["envenenada"]:
            reglas = [h["regla"] for h in res["hallazgos"]]
            eventos.registrar("escudo", "escudo.cuarentena", f"{t.name} · ENVENENADA ({donde}) · {', '.join(reglas)} · «{res['hallazgos'][0]['frase']}»",
                              metodo="tools/list", herramienta=t.name, severidad=4, accion="Denied", disposicion="Quarantined",
                              detalle={"reglas": reglas, "frases": [h["frase"] for h in res["hallazgos"]]})
        else:
            eventos.registrar("escudo", "escudo.aprobada", f"{t.name} · sin órdenes escondidas", metodo="tools/list", herramienta=t.name,
                              accion="Allowed", disposicion="Allowed", detalle={"huella": item["huella"]})
    return {"url": url, "servidor": nombre, "version": version, "sesion": eventos.sesion_actual()["sesion"],
            "total": len(informe), "envenenadas": sum(i["envenenada"] for i in informe), "herramientas": informe}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    try:
        r = probar(sys.argv[1])
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False) if "--json" in sys.argv else f"Error: {e}")
        sys.exit(1)
    if "--json" in sys.argv:
        print(json.dumps(r, ensure_ascii=False))
    else:
        print(f"{r['servidor']} · {r['total']} herramientas · {r['envenenadas']} envenenadas")
        for i in r["herramientas"]:
            print(f"  {'✗ ENVENENADA' if i['envenenada'] else '✓ limpia    '} {i['herramienta']}" +
                  (f" · {', '.join(h['regla'] for h in i['hallazgos'])}" if i["envenenada"] else ""))
