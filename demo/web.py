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
import urllib.parse
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "demo"))
from escudo import analizar  # noqa: E402
from escudo.informe import redactar  # noqa: E402
from escudo.secretos import buscar_secreto  # noqa: E402
from demo import herramientas, mcpaudit, mcpscan  # noqa: E402

sys.path.insert(0, str(RAIZ / "laboratorio"))
import eventos  # noqa: E402

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


PY_LAB = RAIZ / ".venv-scanners" / ("Scripts" if sys.platform == "win32" else "bin") / ("python.exe" if sys.platform == "win32" else "python")


def lab_estado(sesion):
    """Eventos estandarizados del laboratorio, sesiones disponibles y puntos clave de la sesión elegida."""
    todos = eventos.leer()
    sesiones = []
    for e in todos:
        if e["sesion"] not in sesiones:
            sesiones.append(e["sesion"])
    actual = sesion or eventos.sesion_actual()["sesion"]
    if actual not in sesiones:
        sesiones.append(actual)  # una sesión recién creada todavía no tiene eventos
    lista = [e for e in todos if e["sesion"] == actual]
    quiebre, defensa = eventos.puntos_clave(lista)
    servicios = {}
    for nombre, url in (("conector", "http://127.0.0.1:9100/mcp"), ("escudo", "http://127.0.0.1:9200/mcp")):
        try:
            urllib.request.urlopen(url, timeout=1)
            servicios[nombre] = True
        except urllib.error.HTTPError:
            servicios[nombre] = True  # responde, aunque rechace un GET sin cabeceras MCP
        except Exception:
            servicios[nombre] = False
    return {"sesion": actual, "sesiones": sesiones[::-1], "eventos": lista, "servicios": servicios,
            "quiebre": quiebre and quiebre["span_id"], "defensa": defensa and defensa["span_id"]}


def lab_escenario(clave):
    r = subprocess.run([str(PY_LAB), str(RAIZ / "laboratorio" / "prueba_automatica.py"), "--escenario", clave],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180, cwd=str(RAIZ))
    if r.returncode != 0:
        raise RuntimeError("El escenario falló. Revisa que el conector (:9100) y el escudo (:9200) estén corriendo.")
    return {"ok": True, "sesion": eventos.sesion_actual()["sesion"]}


def ideas_analizar(texto):
    """Capas 1 a 3 del escudo sobre un texto: normalización, intención y huella."""
    import hashlib
    res = analizar(texto)
    return {"normalizado": res["normalizado"], "hallazgos": res["hallazgos"], "disfraz": res["disfraz"],
            "envenenada": res["envenenada"], "huella": hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16],
            "invisibles": sum(texto.count(c) for c in "​‌‍⁠﻿­")}


def ideas_hallazgo():
    """Detección por variante en los sets de desarrollo y de prueba, leída de los CSV oficiales."""
    salida = {}
    for conjunto in ("desarrollo", "prueba"):
        ruta = RAIZ / "bench" / f"resultados_{conjunto}.csv"
        if not ruta.exists():
            continue
        filas = [f for f in csv.DictReader(ruta.read_text(encoding="utf-8").splitlines()) if f["envenenada"] == "True"]
        salida[conjunto] = {v: {c: [sum(f[c] == "True" for f in filas if f["variante"] == v), sum(1 for f in filas if f["variante"] == v)]
                                for c in ("mcpscan", "mcpaudit", "escudo")}
                            for v in ("en", "es", "spanglish", "disfrazada")}
    return salida


def probar_conector(url):
    """Corre laboratorio/probar_conector.py (solo lee las descripciones del conector)."""
    r = subprocess.run([str(PY_LAB), str(RAIZ / "laboratorio" / "probar_conector.py"), url, "--json"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60, cwd=str(RAIZ))
    linea = next((l for l in reversed(r.stdout.splitlines()) if l.startswith("{")), "")
    datos = json.loads(linea) if linea else {"error": "La prueba del conector no devolvió resultado."}
    if "error" in datos:
        raise RuntimeError(datos["error"])
    return datos


def lab_reiniciar():
    for url in ("http://127.0.0.1:9100/reiniciar", "http://127.0.0.1:9200/reiniciar"):
        try:
            urllib.request.urlopen(urllib.request.Request(url, method="POST"), timeout=3)
        except Exception:
            pass


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
        ruta = urllib.parse.urlparse(self.path)
        if ruta.path == "/api/lab/estado":
            sesion = urllib.parse.parse_qs(ruta.query).get("sesion", [None])[0]
            return self._json(lab_estado(sesion))
        paginas = {"/": "simulacion.html", "/simulacion": "simulacion.html", "/escanear": "index.html", "/index.html": "index.html",
                   "/laboratorio": "laboratorio.html", "/conectores": "conectores.html", "/alertas.js": "alertas.js",
                   "/ideas": "ideas.html"}
        if self.path in paginas:
            cuerpo = (WEB / paginas[self.path]).read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/javascript; charset=utf-8" if self.path.endswith(".js") else "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.end_headers()
            self.wfile.write(cuerpo)
        elif self.path == "/api/ejemplos":
            self._json(ejemplos())
        elif self.path == "/api/ideas/hallazgo":
            self._json(ideas_hallazgo())
        elif self.path == "/api/resultados":
            self._json(resultados())
        else:
            self._json({"error": "No existe esa ruta."}, 404)

    def do_POST(self):
        largo = int(self.headers.get("Content-Length", 0))
        if self.path in ("/api/ideas/analizar", "/api/ideas/argumentos"):
            if largo > MAX_CARACTERES * 4:
                return self._json({"error": f"El texto supera los {MAX_CARACTERES} caracteres."}, 413)
            texto = str(json.loads(self.rfile.read(largo) or b"{}").get("texto", ""))[:MAX_CARACTERES]
            if self.path == "/api/ideas/analizar":
                return self._json(ideas_analizar(texto))
            secreto = buscar_secreto(texto)
            return self._json({"bloqueado": bool(secreto), "coincidencia": secreto})
        if self.path == "/api/conectores/probar":
            try:
                url = str(json.loads(self.rfile.read(largo) or b"{}").get("url", "")).strip() if largo < 2000 else ""
                if not url:
                    return self._json({"error": "Escribe la URL del conector, por ejemplo http://127.0.0.1:9100/mcp"}, 400)
                return self._json(probar_conector(url))
            except Exception as e:
                return self._json({"error": str(e)}, 502)
        if self.path.startswith("/api/lab/"):
            try:
                pedido = json.loads(self.rfile.read(largo) or b"{}") if largo < 1000 else {}
                if self.path == "/api/lab/escenario" and pedido.get("escenario") in ("A", "B", "C", "D"):
                    return self._json(lab_escenario(pedido["escenario"]))
                if self.path == "/api/lab/sesion":
                    nombre = "".join(c for c in str(pedido.get("nombre", "Cursor")) if c.isalnum() or c in "-_")[:40] or "Cursor"
                    lab_reiniciar()
                    return self._json(eventos.nueva_sesion(f"{nombre}-{__import__('datetime').datetime.now():%H%M%S}"))
                if self.path == "/api/lab/reiniciar":
                    lab_reiniciar()
                    return self._json({"ok": True})
                return self._json({"error": "Pedido no válido."}, 400)
            except Exception as e:
                return self._json({"error": str(e)}, 500)
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
    puerto = int(sys.argv[sys.argv.index("--puerto") + 1]) if "--puerto" in sys.argv else PUERTO
    print(f"Demo del Escudo MCP en español → http://127.0.0.1:{puerto}  (Ctrl+C para salir)")
    ThreadingHTTPServer(("127.0.0.1", puerto), Manejador).serve_forever()
