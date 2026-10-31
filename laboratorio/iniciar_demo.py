"""Arranca toda la demo con un comando: conector malicioso, Escudo verificador y la web.

Antes de arrancar revisa que esté el entorno .venv-scanners, que los puertos estén libres
(o que ya los ocupen nuestros propios servicios) y espera a que cada servicio responda.
Ctrl+C detiene todo lo que se levantó.

Uso (desde la carpeta escudo-mcp-es, con cualquier Python 3.10+):
  python laboratorio/iniciar_demo.py
  python laboratorio/iniciar_demo.py --limpiar     # archiva los logs anteriores y empieza de cero
"""
import datetime as dt
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
WIN = sys.platform == "win32"
VENV = RAIZ / ".venv-scanners" / ("Scripts" if WIN else "bin")
PY_VENV = VENV / ("python.exe" if WIN else "python")
LOGS = RAIZ / "laboratorio" / "logs"
SERVICIOS = [
    ("Conector malicioso", 9100, "http://127.0.0.1:9100/mcp", [str(PY_VENV), "laboratorio/servidor_malicioso.py"]),
    ("Escudo verificador", 9200, "http://127.0.0.1:9200/mcp", [str(PY_VENV), "laboratorio/verificador.py"]),
    ("Demo web", 8770, "http://127.0.0.1:8770/api/lab/estado", [sys.executable, "-X", "utf8", "demo/web.py", "--puerto", "8770"]),
]
VERDE, ROJO, AMARILLO, GRIS, FIN = "\033[32m", "\033[31m", "\033[33m", "\033[90m", "\033[0m"


def puerto_ocupado(puerto):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", puerto)) == 0


def responde(url):
    try:
        urllib.request.urlopen(url, timeout=2)
        return True
    except urllib.error.HTTPError:
        return True   # contestó, aunque rechace un GET simple (MCP pide cabeceras propias)
    except Exception:
        return False


def chequeos():
    problemas = []
    if not PY_VENV.exists():
        problemas.append(f"Falta el entorno .venv-scanners. Créalo con:\n    python -m venv .venv-scanners\n"
                         f"    {PY_VENV} -m pip install -r requirements-scanners.txt")
    elif subprocess.run([str(PY_VENV), "-c", "import mcp, uvicorn, starlette"], capture_output=True).returncode != 0:
        problemas.append(f"Al entorno le falta el SDK de MCP. Instálalo con:\n    {PY_VENV} -m pip install -r requirements-scanners.txt")
    for nombre in ("laboratorio/servidor_malicioso.py", "laboratorio/verificador.py", "demo/web.py"):
        if not (RAIZ / nombre).exists():
            problemas.append(f"No encuentro {nombre}. Corre este comando desde la carpeta escudo-mcp-es.")
    return problemas


def main():
    if WIN:
        import os
        os.system("")
        sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(line_buffering=True)  # que cada línea se vea al momento, también en terminales integradas
    print("Escudo MCP · arranque de la demo\n")
    problemas = chequeos()
    if problemas:
        for p in problemas:
            print(f"{ROJO}✗{FIN} {p}")
        sys.exit(1)
    print(f"{VERDE}✓{FIN} Entorno .venv-scanners con el SDK de MCP")

    if "--limpiar" in sys.argv and LOGS.exists():
        archivo = LOGS.parent / f"logs-{dt.datetime.now():%Y%m%d-%H%M%S}"
        shutil.move(str(LOGS), str(archivo))
        print(f"{VERDE}✓{FIN} Logs anteriores archivados en {archivo.relative_to(RAIZ)}")

    propios = []
    try:
        for nombre, puerto, url, comando in SERVICIOS:
            if puerto_ocupado(puerto):
                if responde(url):
                    print(f"{AMARILLO}•{FIN} {nombre}: ya estaba corriendo en :{puerto}, se reutiliza")
                    continue
                print(f"{ROJO}✗{FIN} El puerto {puerto} está ocupado por otro programa. Ciérralo y vuelve a intentar.")
                raise SystemExit(1)
            propios.append(subprocess.Popen(comando, cwd=str(RAIZ), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
            for _ in range(60):
                if responde(url):
                    break
                time.sleep(0.25)
            else:
                print(f"{ROJO}✗{FIN} {nombre} no respondió en :{puerto}. Prueba a correrlo solo para ver el error:\n    {' '.join(comando)}")
                raise SystemExit(1)
            print(f"{VERDE}✓{FIN} {nombre} en :{puerto}")

        print(f"""
{VERDE}Todo listo.{FIN} Abre en el navegador:
  Laboratorio en vivo   http://127.0.0.1:8770/laboratorio
  Probar conectores     http://127.0.0.1:8770/conectores
  Simulación            http://127.0.0.1:8770/
{GRIS}Para Cursor: carpetas en laboratorio/carpetas-cursor (python laboratorio/preparar.py).
Ctrl+C detiene lo que se levantó desde aquí.{FIN}""")
        while all(p.poll() is None for p in propios):
            time.sleep(1)
        caidos = [p for p in propios if p.poll() is not None]
        if caidos:
            print(f"{ROJO}✗{FIN} Un servicio se detuvo inesperadamente. Se detiene la demo.")
    except KeyboardInterrupt:
        print("\nDeteniendo la demo…")
    finally:
        for p in propios:
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    p.kill()
        print("Listo.")


if __name__ == "__main__":
    main()
