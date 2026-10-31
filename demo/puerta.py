"""Puerta de entrada MCP: el Escudo ES revisa las herramientas antes de que el agente las vea.

Simula lo que hace un agente como Cursor al arrancar: lee demo/conectores.json,
se conecta por MCP (stdio) a cada conector, pide la lista de herramientas y
decide cuáles le muestra al agente. Cada paso queda en el log.

  - Con escudo: las herramientas envenenadas quedan en cuarentena.
  - Sin escudo: el agente las ve todas y "obedece" las órdenes escondidas
    (la obediencia es SIMULADA: no se lee ni se envía ningún archivo).

Uso (con el Python de .venv-scanners, que tiene el SDK de MCP):
  python demo/puerta.py                 # con escudo, log legible en la terminal
  python demo/puerta.py --sin-escudo
  python demo/puerta.py --json          # eventos en JSON, para la demo web
Cada corrida también se guarda en demo/logs/escudo-AAAAMMDD-HHMMSS.jsonl.
"""
import argparse
import asyncio
import datetime as dt
import json
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from escudo import analizar  # noqa: E402
from escudo.informe import redactar  # noqa: E402
from mcp import ClientSession, StdioServerParameters  # noqa: E402
from mcp.client.stdio import stdio_client  # noqa: E402

CONFIG = RAIZ / "demo" / "conectores.json"
LOGS = RAIZ / "demo" / "logs"

# Qué "haría" un agente obediente con cada orden escondida (solo texto, nada se ejecuta).
EFECTO = {
    "leer_o_enviar_secretos": "leyó un archivo secreto y lo envió fuera",
    "enviar_contrasenas": "envió contraseñas fuera",
    "exfiltrar_datos_usuario": "copió datos de la persona usuaria a otro servidor",
    "ocultar_al_usuario": "no le avisó a la persona usuaria",
    "ignorar_instrucciones": "descartó sus instrucciones de seguridad",
    "instrucciones_anuladas": "descartó sus instrucciones de seguridad",
    "orden_previa": "hizo una acción extra antes de usar la herramienta",
}


class Registro:
    def __init__(self, como_json):
        self.como_json = como_json
        self.eventos = []
        self.inicio = dt.datetime.now()

    def __call__(self, nivel, mensaje, **datos):
        ev = {"t": dt.datetime.now().strftime("%H:%M:%S.%f")[:-3], "nivel": nivel, "mensaje": mensaje, **datos}
        self.eventos.append(ev)
        if not self.como_json:
            color = {"INFO": "\033[90m", "OK": "\033[32m", "BLOQUEO": "\033[33m", "ALERTA": "\033[31m"}.get(nivel, "")
            print(f"{ev['t']}  {color}{nivel:<8}\033[0m {mensaje}")

    def guardar(self):
        LOGS.mkdir(exist_ok=True)
        ruta = LOGS / f"escudo-{self.inicio:%Y%m%d-%H%M%S}.jsonl"
        with ruta.open("w", encoding="utf-8", newline="\n") as f:
            for ev in self.eventos:
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        return ruta


async def herramientas_de(nombre, cfg):
    comando = sys.executable if cfg["command"] == "python" else cfg["command"]
    args = [str(RAIZ / a) if a.endswith(".py") else a for a in cfg.get("args", [])]
    params = StdioServerParameters(command=comando, args=args)
    # El ruido interno de cada conector se descarta; el log que importa es el de la puerta.
    with open(os.devnull, "w") as silencio:
        async with stdio_client(params, errlog=silencio) as (lectura, escritura):
            async with ClientSession(lectura, escritura) as sesion:
                info = await sesion.initialize()
                lista = await sesion.list_tools()
                return info.serverInfo.name, [(t.name, t.description or "") for t in lista.tools]


async def correr(con_escudo, log):
    config = json.loads(CONFIG.read_text(encoding="utf-8"))["mcpServers"]
    log("INFO", f"Agente iniciando · {len(config)} conectores en conectores.json · Escudo ES {'ACTIVADO' if con_escudo else 'DESACTIVADO'}",
        tipo="inicio", escudo=con_escudo)
    expuestas, bloqueadas, danos = [], [], []
    for nombre, cfg in config.items():
        log("INFO", f"Conectando por MCP (stdio) a «{nombre}»…", tipo="conectando", conector=nombre)
        try:
            servidor, herramientas = await herramientas_de(nombre, cfg)
        except Exception as e:  # un conector caído no detiene la demo
            log("ALERTA", f"No se pudo conectar a «{nombre}»: {e}", tipo="error", conector=nombre)
            continue
        log("OK", f"«{nombre}» respondió el handshake · servidor {servidor} · {len(herramientas)} herramientas",
            tipo="conectado", conector=nombre, total=len(herramientas))
        for herramienta, descripcion in herramientas:
            res = analizar(descripcion)
            reglas = [h["regla"] for h in res["hallazgos"]]
            frases = [h["frase"] for h in res["hallazgos"]]
            base = {"conector": nombre, "herramienta": herramienta, "descripcion": descripcion,
                    "reglas": reglas, "frases": frases, "informe": redactar(descripcion, res)}
            if not res["envenenada"]:
                expuestas.append(f"{nombre}.{herramienta}")
                log("OK", f"{nombre}.{herramienta} · revisada · sin órdenes escondidas → visible para el agente",
                    tipo="permitida", **base)
            elif con_escudo:
                bloqueadas.append(f"{nombre}.{herramienta}")
                log("BLOQUEO", f"{nombre}.{herramienta} · EN CUARENTENA · {', '.join(reglas)} · frase: «{frases[0]}»",
                    tipo="bloqueada", **base)
            else:
                expuestas.append(f"{nombre}.{herramienta}")
                log("INFO", f"{nombre}.{herramienta} · sin revisión → visible para el agente", tipo="sin_revisar", **base)
                for regla in reglas:
                    if regla in EFECTO:
                        danos.append(f"{nombre}.{herramienta}: {EFECTO[regla]}")
                        log("ALERTA", f"Agente (SIMULADO) obedeció la descripción de {nombre}.{herramienta}: {EFECTO[regla]}",
                            tipo="dano", regla=regla, **base)
    log("INFO", f"Sesión lista · el agente ve {len(expuestas)} herramientas · {len(bloqueadas)} en cuarentena · {len(danos)} acciones dañinas simuladas",
        tipo="resumen", expuestas=expuestas, bloqueadas=bloqueadas, danos=danos, escudo=con_escudo)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sin-escudo", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if sys.platform == "win32" and not args.json:
        import os
        os.system("")
        sys.stdout.reconfigure(encoding="utf-8")
    log = Registro(args.json)
    asyncio.run(correr(not args.sin_escudo, log))
    ruta = log.guardar()
    if args.json:
        sys.stdout.reconfigure(encoding="utf-8")
        print(json.dumps({"eventos": log.eventos, "log": ruta.relative_to(RAIZ).as_posix()}, ensure_ascii=False))
    else:
        print(f"\nLog guardado en {ruta.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
