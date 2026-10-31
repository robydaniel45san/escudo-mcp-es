"""Demo visual del pitch: servidor web local, sin dependencias externas.

Corre los escáneres reales (mcpscan y mcp-audit) y el Escudo ES sobre una
descripción de herramienta MCP y muestra el resultado en el navegador.
Solo escucha en 127.0.0.1.

Uso:  python demo/web.py            → http://127.0.0.1:8765
"""
import csv
import json
import subprocess
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "demo"))
from escudo import analizar  # noqa: E402
from escudo.informe import redactar  # noqa: E402
from demo import herramientas, mcpaudit, mcpscan  # noqa: E402

PUERTO = 8765
WEB = RAIZ / "demo" / "web"
MAX_CARACTERES = 2000

PLANTILLA = '''from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo_web")


@mcp.tool()
def herramienta(texto: str = "") -> str:
    """{descripcion}"""
    return "ok"


if __name__ == "__main__":
    mcp.run()
'''


def ejemplos():
    """Casos para el selector: la herramienta del IVA y el set de prueba congelado."""
    lista = [{"id": "IVA", "titulo": "Demo del pitch: calcular IVA (spanglish)", "variante": "spanglish", "envenenada": True,
              "descripcion": " ".join(dict(herramientas(RAIZ / "demo" / "servidor_iva.py"))["calcular_iva"].split())}]
    nombres = {"en": "Inglés", "es": "Español", "spanglish": "Spanglish", "disfrazada": "Disfrazada"}
    for linea in (RAIZ / "dataset" / "casos_prueba.jsonl").read_text(encoding="utf-8").splitlines():
        c = json.loads(linea)
        estado = "envenenada" if c["envenenada"] else "limpia"
        lista.append({"id": c["id"], "titulo": f"{c['id']} · {nombres[c['variante']]} · {estado}",
                      "variante": c["variante"], "envenenada": c["envenenada"], "descripcion": c["descripcion"]})
    return lista


def resultados():
    """Detección por variante leída del CSV oficial del set de prueba."""
    ruta = RAIZ / "bench" / "resultados_prueba.csv"
    if not ruta.exists():
        return None
    filas = list(csv.DictReader(ruta.read_text(encoding="utf-8").splitlines()))
    columnas = ["mcpscan", "mcpaudit", "escudo", "mcpscan_escudo", "mcpaudit_escudo"]
    salida = {}
    for v in ["en", "es", "spanglish", "disfrazada", "total"]:
        sub = [f for f in filas if v == "total" or f["variante"] == v]
        env = [f for f in sub if f["envenenada"] == "True"]
        lim = [f for f in sub if f["envenenada"] != "True"]
        salida[v] = {c: {"detecta": sum(f[c] == "True" for f in env), "envenenadas": len(env),
                         "falsas": sum(f[c] == "True" for f in lim), "limpias": len(lim)} for c in columnas}
    return salida


def escanear(descripcion):
    with tempfile.TemporaryDirectory(prefix="escudo-web-") as tmp:
        ruta = Path(tmp) / "herramienta.py"
        # Se escapan barras y comillas para que el texto nunca salga del docstring.
        seguro = descripcion.replace("\\", "\\\\").replace('"', '\\"')
        ruta.write_text(PLANTILLA.format(descripcion=seguro), encoding="utf-8")
        try:
            hs = mcpscan(ruta)
            scan = {"envenenada": bool(hs), "hallazgos": [f"{h['rule_id']}: {h['snippet']}" for h in hs]}
        except Exception as e:  # el escáner puede fallar; la demo sigue
            scan = {"error": str(e)}
        try:
            ha = mcpaudit(ruta)
            audit = {"envenenada": bool(ha), "hallazgos": [f"{h['title']} ({h.get('evidence', '')})" for h in ha]}
        except Exception as e:
            audit = {"error": str(e)}
    esc = analizar(descripcion)
    return {"mcpscan": scan, "mcpaudit": audit, "escudo": esc, "informe": redactar(descripcion, esc, scan, audit)}


def simular(con_escudo):
    """Corre la puerta de entrada MCP (demo/puerta.py) con el Python que tiene el SDK de MCP."""
    py = RAIZ / ".venv-scanners" / ("Scripts" if sys.platform == "win32" else "bin") / ("python.exe" if sys.platform == "win32" else "python")
    args = [str(py), str(RAIZ / "demo" / "puerta.py"), "--json"] + ([] if con_escudo else ["--sin-escudo"])
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180, cwd=str(RAIZ))
    if r.returncode != 0:
        raise RuntimeError("La simulación falló. " + r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "La simulación falló.")
    return json.loads(r.stdout)


class Manejador(BaseHTTPRequestHandler):
    def _json(self, datos, codigo=200):
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        paginas = {"/": "simulacion.html", "/simulacion": "simulacion.html", "/escanear": "index.html", "/index.html": "index.html"}
        if self.path in paginas:
            cuerpo = (WEB / paginas[self.path]).read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)
        elif self.path == "/api/ejemplos":
            self._json(ejemplos())
        elif self.path == "/api/resultados":
            self._json(resultados())
        else:
            self._json({"error": "No existe esa ruta."}, 404)

    def do_POST(self):
        largo = int(self.headers.get("Content-Length", 0))
        if self.path == "/api/simular":
            try:
                pedido = json.loads(self.rfile.read(largo) or b"{}") if largo < 1000 else {}
                return self._json(simular(bool(pedido.get("escudo", True))))
            except Exception as e:
                return self._json({"error": str(e)}, 500)
        if self.path != "/api/escanear":
            return self._json({"error": "No existe esa ruta."}, 404)
        if largo > MAX_CARACTERES * 4:
            return self._json({"error": f"La descripción supera los {MAX_CARACTERES} caracteres."}, 413)
        try:
            descripcion = json.loads(self.rfile.read(largo) or b"{}").get("descripcion", "").strip()
        except json.JSONDecodeError:
            return self._json({"error": "No se pudo leer el pedido."}, 400)
        if not descripcion:
            return self._json({"error": "Escribe o elige una descripción para escanear."}, 400)
        if len(descripcion) > MAX_CARACTERES:
            return self._json({"error": f"La descripción supera los {MAX_CARACTERES} caracteres."}, 413)
        self._json(escanear(descripcion))

    def log_message(self, formato, *args):
        sys.stderr.write("· " + (formato % args) + "\n")


if __name__ == "__main__":
    print(f"Demo del Escudo MCP en español → http://127.0.0.1:{PUERTO}  (Ctrl+C para salir)")
    ThreadingHTTPServer(("127.0.0.1", PUERTO), Manejador).serve_forever()
