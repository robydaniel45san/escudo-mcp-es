"""Escudo verificador MCP: un intermediario entre el agente (Cursor) y un conector.

El agente se conecta a http://127.0.0.1:9200/mcp en lugar de al conector. Por cada pedido:

  1. Lista de herramientas: pide la lista al conector y la pasa por el Escudo ES.
     Solo deja ver las limpias. Las envenenadas quedan en cuarentena.
  2. Huella de cada descripción aprobada (SHA-256). Si después cambia (rug pull),
     la herramienta queda en cuarentena aunque la nueva descripción parezca limpia.
  3. Llamadas: antes de reenviarlas, vuelve a comprobar la descripción y revisa los
     argumentos. Si llevan algo con forma de secreto (claves, el canario, llaves
     privadas), bloquea la llamada: posible exfiltración.

Todo queda en laboratorio/logs/verificador.jsonl y en la terminal.

Uso (con el Python de .venv-scanners):
  python laboratorio/verificador.py                         # conector en :9100
  python laboratorio/verificador.py --conector http://127.0.0.1:9100/mcp --puerto 9200
"""
import argparse
import contextlib
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

import mcp.types as types
import uvicorn
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
from escudo import analizar  # noqa: E402

sys.path.insert(0, str(AQUI))
import eventos  # noqa: E402

LOG = AQUI / "logs" / "verificador.jsonl"
# Argumentos con forma de secreto: el canario del laboratorio, claves típicas y llaves privadas.
SECRETO = re.compile(r"CANARIO-[A-Z0-9-]+|(api[_-]?key|password|secret|token|contrasena)\s*[=:]\s*\S+|"
                     r"sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----", re.I)

COLOR = {"OK": "\033[32m", "BLOQUEO": "\033[33m", "ALERTA": "\033[31m", "INFO": "\033[90m"}


def anotar(nivel, mensaje, **datos):
    LOG.parent.mkdir(exist_ok=True)
    registro = {"t": dt.datetime.now().isoformat(timespec="milliseconds"), "nivel": nivel, "mensaje": mensaje, **datos}
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(registro, ensure_ascii=False) + "\n")
    print(f"[escudo] {registro['t'][11:23]} {COLOR.get(nivel, '')}{nivel:<8}\033[0m {mensaje}", flush=True)
    # Registro estandarizado (OpenTelemetry MCP + OCSF) para el tablero.
    tipo, herramienta = datos.get("tipo"), datos.get("herramienta")
    mapa = {
        "lista": ("escudo.lista", "tools/list", 1, None, None),
        "aprobada": ("escudo.aprobada", "tools/list", 1, "Allowed", "Allowed"),
        "cuarentena": ("escudo.cuarentena", "tools/list", 4, "Denied", "Quarantined"),
        "rug_pull": ("escudo.rug_pull", "tools/list", 4, "Denied", "Quarantined"),
        "llamada": ("escudo.llamada_reenviada", "tools/call", 1, "Allowed", "Allowed"),
        "llamada_bloqueada": ("escudo.llamada_bloqueada", "tools/call", 4, "Denied", "Blocked"),
        "desconocida": ("escudo.llamada_bloqueada", "tools/call", 3, "Denied", "Blocked"),
        "exfiltracion_bloqueada": ("escudo.exfiltracion_bloqueada", "tools/call", 4, "Denied", "Blocked"),
    }
    if tipo in mapa:
        evento, metodo, sev, accion, disp = mapa[tipo]
        detalle = {k: datos[k] for k in ("reglas", "frases", "huella", "visibles", "total", "descripcion") if k in datos}
        eventos.registrar("escudo", evento, mensaje, metodo=metodo, herramienta=herramienta, severidad=sev,
                          accion=accion, disposicion=disp, argumentos=datos.get("argumentos"), detalle=detalle or None)


def huella(texto):
    return hashlib.sha256((texto or "").encode("utf-8")).hexdigest()[:16]


class Verificador:
    def __init__(self, conector):
        self.conector = conector
        self.aprobadas = {}     # nombre -> huella de la descripción aprobada
        self.cuarentena = {}    # nombre -> motivo

    @contextlib.asynccontextmanager
    async def sesion(self):
        async with streamablehttp_client(self.conector) as (lectura, escritura, _):
            async with ClientSession(lectura, escritura) as s:
                await s.initialize()
                yield s

    def revisar(self, herramienta):
        """Decide si una herramienta puede llegar al agente. Devuelve (permitida, motivo)."""
        nombre, desc = herramienta.name, herramienta.description or ""
        h = huella(desc)
        if nombre in self.aprobadas and self.aprobadas[nombre] != h:
            motivo = f"rug pull: la descripción cambió después de aprobarla ({self.aprobadas[nombre]} → {h})"
            self.cuarentena[nombre] = motivo
            del self.aprobadas[nombre]
            anotar("ALERTA", f"{nombre} · {motivo}", herramienta=nombre, tipo="rug_pull", descripcion=desc)
            return False, motivo
        if nombre in self.cuarentena:
            return False, self.cuarentena[nombre]
        res = analizar(desc)
        if res["envenenada"]:
            reglas = ", ".join(x["regla"] for x in res["hallazgos"])
            frase = res["hallazgos"][0]["frase"]
            motivo = f"Escudo ES: {reglas} · «{frase}»"
            self.cuarentena[nombre] = motivo
            anotar("BLOQUEO", f"{nombre} · EN CUARENTENA · {motivo}", herramienta=nombre, tipo="cuarentena",
                   reglas=[x["regla"] for x in res["hallazgos"]], frases=[x["frase"] for x in res["hallazgos"]], descripcion=desc)
            return False, motivo
        if nombre not in self.aprobadas:
            anotar("OK", f"{nombre} · aprobada · huella {h}", herramienta=nombre, tipo="aprobada", huella=h)
        self.aprobadas[nombre] = h
        return True, ""

    async def listar(self):
        async with self.sesion() as s:
            lista = await s.list_tools()
        # Se reexpone cada herramienta sin outputSchema: el verificador reenvía el contenido tal cual.
        visibles = [t.model_copy(update={"outputSchema": None}) for t in lista.tools if self.revisar(t)[0]]
        anotar("INFO", f"El agente pidió la lista: ve {len(visibles)} de {len(lista.tools)} herramientas",
               tipo="lista", visibles=[t.name for t in visibles], total=len(lista.tools))
        return visibles

    async def llamar(self, nombre, argumentos):
        # Las decisiones se toman dentro de la sesión, pero el error se lanza afuera,
        # así el agente recibe el motivo claro y no un error del cierre de la conexión.
        error, contenido = None, None
        async with self.sesion() as s:
            lista = await s.list_tools()
            actual = next((t for t in lista.tools if t.name == nombre), None)
            if actual is None:
                anotar("BLOQUEO", f"{nombre} · el conector no la ofrece", herramienta=nombre, tipo="desconocida")
                error = f"Escudo ES: la herramienta {nombre} no existe en el conector."
            else:
                permitida, motivo = self.revisar(actual)
                texto = json.dumps(argumentos or {}, ensure_ascii=False)
                secreto = SECRETO.search(texto)
                if not permitida:
                    anotar("BLOQUEO", f"Llamada a {nombre} bloqueada · {motivo}", herramienta=nombre, tipo="llamada_bloqueada")
                    error = f"Escudo ES bloqueó {nombre}: {motivo}"
                elif secreto:
                    visible = secreto.group(0)[:24] + "…"
                    anotar("ALERTA", f"Llamada a {nombre} bloqueada · los argumentos llevan algo con forma de secreto ({visible})",
                           herramienta=nombre, tipo="exfiltracion_bloqueada", argumentos=argumentos)
                    error = f"Escudo ES bloqueó {nombre}: los argumentos parecen contener un secreto. No se envió nada."
                else:
                    anotar("OK", f"Llamada a {nombre} reenviada al conector · argumentos revisados", herramienta=nombre,
                           tipo="llamada", argumentos=argumentos)
                    contenido = (await s.call_tool(nombre, argumentos or {})).content
        if error:
            raise ValueError(error)
        return contenido


def crear_app(verificador):
    servidor = Server("escudo-verificador")

    @servidor.list_tools()
    async def listar() -> list[types.Tool]:
        return await verificador.listar()

    @servidor.call_tool()
    async def llamar(nombre: str, argumentos: dict):
        return await verificador.llamar(nombre, argumentos)

    gestor = StreamableHTTPSessionManager(app=servidor, stateless=True)

    async def manejar(scope, receive, send):
        await gestor.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def ciclo(app):
        async with gestor.run():
            yield

    async def reiniciar(request):
        """Olvida aprobaciones y cuarentenas: cada escenario empieza desde cero."""
        verificador.aprobadas.clear()
        verificador.cuarentena.clear()
        return JSONResponse({"ok": True})

    return Starlette(routes=[Route("/reiniciar", reiniciar, methods=["POST"]), Mount("/mcp", app=manejar)], lifespan=ciclo)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--conector", default="http://127.0.0.1:9100/mcp")
    ap.add_argument("--puerto", type=int, default=9200)
    args = ap.parse_args()
    if sys.platform == "win32":
        import os
        os.system("")
        sys.stdout.reconfigure(encoding="utf-8")
    anotar("INFO", f"Escudo verificador en http://127.0.0.1:{args.puerto}/mcp · protege a {args.conector}", tipo="inicio")
    uvicorn.run(crear_app(Verificador(args.conector)), host="127.0.0.1", port=args.puerto, log_level="warning")


if __name__ == "__main__":
    main()
