"""Mide los escáneres MCP con y sin el Escudo ES y escribe RESULTS.md.

Por cada caso del banco genera un servidor MCP de juguete (una herramienta cuya
descripción es el caso), corre los escáneres de la línea base y el Escudo ES,
y calcula la detección y las falsas alarmas por variante.

Uso:
  python bench/bench.py                       # set de prueba congelado
  python bench/bench.py --set desarrollo
  python bench/bench.py --set todos --sin-mcp-audit
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from escudo import analizar  # noqa: E402

SCRIPTS = RAIZ / ".venv-scanners" / ("Scripts" if sys.platform == "win32" else "bin")
EXE = ".exe" if sys.platform == "win32" else ""
PY_SCANNERS = SCRIPTS / f"python{EXE}"
VARIANTES = ["en", "es", "spanglish", "disfrazada"]
NOMBRE_VARIANTE = {"en": "Inglés", "es": "Español", "spanglish": "Spanglish", "disfrazada": "Disfrazada"}
# Solo cuentan las reglas que analizan la descripción de la herramienta.
REGLAS_MCPSCAN = {"MCP002", "MCP023"}
ANALIZADORES_MCPAUDIT = {"poisoning", "delegation"}

PLANTILLA_SERVIDOR = '''from mcp.server.fastmcp import FastMCP

mcp = FastMCP("{nombre}")


@mcp.tool()
def herramienta(texto: str = "") -> str:
    """{descripcion}"""
    return "ok"


if __name__ == "__main__":
    mcp.run()
'''


def cargar(conjunto):
    archivo = {"prueba": "casos_prueba.jsonl", "desarrollo": "casos_desarrollo.jsonl", "todos": "casos.jsonl",
               "ciego": "casos_ciegos.jsonl"}[conjunto]
    ruta = RAIZ / "dataset" / archivo
    casos = [json.loads(linea) for linea in ruta.read_text(encoding="utf-8").splitlines() if linea.strip()]
    return casos, ruta


def escribir_servidores(casos, carpeta, etiqueta):
    for c in casos:
        desc = c["descripcion"].replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
        nombre = f"caso_{c['id']}_{etiqueta}"
        (carpeta / f"{c['id']}.py").write_text(PLANTILLA_SERVIDOR.format(nombre=nombre, descripcion=desc), encoding="utf-8")


def correr_mcpscan(carpeta):
    exe = SCRIPTS / f"mcpscan{EXE}"
    r = subprocess.run([str(exe), "--json", "--min-severity", "critical", str(carpeta)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    datos = json.loads(r.stdout)
    detectados = defaultdict(list)
    for f in datos.get("findings", []):
        if f.get("rule_id") in REGLAS_MCPSCAN:
            detectados[Path(f["path"]).stem].append(f["rule_id"])
    return detectados, datos.get("files_scanned")


def correr_mcpaudit(casos, carpeta, etiqueta):
    config = {"mcpServers": {f"caso_{c['id']}_{etiqueta}": {"command": str(PY_SCANNERS), "args": [str(carpeta / f"{c['id']}.py")]}
                             for c in casos}}
    ruta_config = carpeta / "mcp.json"
    ruta_config.write_text(json.dumps(config, indent=2), encoding="utf-8")
    exe = SCRIPTS / f"mcp-audit{EXE}"
    r = subprocess.run([str(exe), "scan", str(ruta_config), "--connect", "--format", "json"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800)
    salida = r.stdout[r.stdout.find("{"):]
    datos = json.loads(salida)
    detectados = defaultdict(list)
    for f in datos.get("findings", []):
        if f.get("analyzer") in ANALIZADORES_MCPAUDIT:
            servidor = str(f.get("server", "")).split(":")[0]
            caso = servidor.split("_")[1] if servidor.startswith("caso_") else None
            if caso:
                detectados[caso].append(f.get("title", f.get("id")))
    conectados = len(datos.get("servers", []) or [])
    return detectados, conectados


def metricas(filas, columna):
    por_variante = {}
    for v in VARIANTES + ["total"]:
        sub = [f for f in filas if v == "total" or f["variante"] == v]
        env = [f for f in sub if f["envenenada"]]
        lim = [f for f in sub if not f["envenenada"]]
        por_variante[v] = (sum(f[columna] for f in env), len(env), sum(f[columna] for f in lim), len(lim))
    return por_variante


def frac(a, b):
    return f"{a}/{b} ({round(100 * a / b) if b else 0} %)"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--set", default="prueba", choices=["prueba", "desarrollo", "todos", "ciego"])
    ap.add_argument("--sin-mcp-audit", action="store_true", help="omite mcp-audit (más rápido)")
    ap.add_argument("--out", default=None, help="ruta de RESULTS.md (por defecto, solo con --set prueba)")
    args = ap.parse_args()

    casos, ruta = cargar(args.set)
    huella = hashlib.sha256(ruta.read_bytes()).hexdigest()
    etiqueta = dt.datetime.now().strftime("%H%M%S")
    print(f"Banco: {ruta.name} · {len(casos)} casos · sha256 {huella[:12]}…")

    with tempfile.TemporaryDirectory(prefix="escudo-bench-") as tmp:
        carpeta = Path(tmp)
        escribir_servidores(casos, carpeta, etiqueta)
        print("Corriendo mcpscan…")
        det_scan, archivos = correr_mcpscan(carpeta)
        det_audit, conectados = ({}, 0)
        if not args.sin_mcp_audit:
            print("Corriendo mcp-audit --connect (levanta un servidor por caso)…")
            det_audit, conectados = correr_mcpaudit(casos, carpeta, etiqueta)

    filas = []
    for c in casos:
        esc = analizar(c["descripcion"])
        f = {
            "id": c["id"], "variante": c["variante"], "envenenada": c["envenenada"], "tecnica": c["tecnica"],
            "mcpscan": bool(det_scan.get(c["id"])),
            "mcpaudit": bool(det_audit.get(c["id"])),
            "escudo": esc["envenenada"],
            "reglas_escudo": ";".join(h["regla"] for h in esc["hallazgos"]),
            "reglas_mcpscan": ";".join(det_scan.get(c["id"], [])),
            "hallazgos_mcpaudit": ";".join(det_audit.get(c["id"], [])),
        }
        f["mcpscan_escudo"] = f["mcpscan"] or f["escudo"]
        f["mcpaudit_escudo"] = f["mcpaudit"] or f["escudo"]
        filas.append(f)

    salida_csv = RAIZ / "bench" / f"resultados_{args.set}.csv"
    with salida_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)

    columnas = [("mcpscan", "mcpscan"), ("mcpscan_escudo", "mcpscan + Escudo ES")]
    if not args.sin_mcp_audit:
        columnas += [("mcpaudit", "mcp-audit"), ("mcpaudit_escudo", "mcp-audit + Escudo ES")]
    columnas.append(("escudo", "Escudo ES solo"))
    m = {col: metricas(filas, col) for col, _ in columnas}

    for col, nombre in columnas:
        t = m[col]["total"]
        print(f"{nombre:26s} detecta {frac(t[0], t[1]):>12s} · falsas alarmas {frac(t[2], t[3])}")
    print(f"CSV: {salida_csv.relative_to(RAIZ)}")

    destino = Path(args.out) if args.out else (RAIZ / "RESULTS.md" if args.set == "prueba" else None)
    if destino:
        destino.write_text(informe(args, casos, ruta, huella, columnas, m, filas, archivos, conectados), encoding="utf-8")
        print(f"Informe: {destino}")


def informe(args, casos, ruta, huella, columnas, m, filas, archivos, conectados):
    hoy = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    L = ["# Resultados", "",
         f"> Generado por `bench/bench.py --set {args.set}` el {hoy}. Ningún número se escribe a mano.", "",
         f"- Banco: `dataset/{ruta.name}` · {len(casos)} casos · SHA-256 `{huella}`",
         f"- mcpscan: {archivos} archivos analizados · reglas contadas: {', '.join(sorted(REGLAS_MCPSCAN))}"]
    if not args.sin_mcp_audit:
        L.append(f"- mcp-audit `--connect`: {conectados} servidores conectados · analizadores contados: {', '.join(sorted(ANALIZADORES_MCPAUDIT))}")
    L += ["- Escudo ES: normalización + reglas bilingües (`escudo/`)", "",
          "## Ataques detectados por variante", "",
          "| Variante | " + " | ".join(n for _, n in columnas) + " |",
          "|---|" + "---|" * len(columnas)]
    for v in VARIANTES + ["total"]:
        nombre = "**Total**" if v == "total" else NOMBRE_VARIANTE[v]
        L.append(f"| {nombre} | " + " | ".join(frac(m[c][v][0], m[c][v][1]) for c, _ in columnas) + " |")
    L += ["", "## Falsas alarmas (casos limpios marcados como envenenados)", "",
          "| Variante | " + " | ".join(n for _, n in columnas) + " |",
          "|---|" + "---|" * len(columnas)]
    for v in VARIANTES + ["total"]:
        nombre = "**Total**" if v == "total" else NOMBRE_VARIANTE[v]
        L.append(f"| {nombre} | " + " | ".join(frac(m[c][v][2], m[c][v][3]) for c, _ in columnas) + " |")
    L += ["", "## Detalle por caso", "",
          "| Caso | Variante | Real | " + " | ".join(n for _, n in columnas) + " | Reglas del Escudo ES |",
          "|---|---|---|" + "---|" * len(columnas) + "---|"]
    for f in filas:
        real = "envenenada" if f["envenenada"] else "limpia"
        celdas = []
        for c, _ in columnas:
            if f[c] and f["envenenada"]:
                celdas.append("✅ detecta")
            elif f[c]:
                celdas.append("⚠️ falsa alarma")
            elif f["envenenada"]:
                celdas.append("❌ no la ve")
            else:
                celdas.append("· limpia")
        L.append(f"| {f['id']} | {NOMBRE_VARIANTE[f['variante']]} | {real} | " + " | ".join(celdas) + f" | {f['reglas_escudo'] or '·'} |")
    # Cada set tiene sus propios hallazgos: bench/hallazgos.md (prueba) o bench/hallazgos_<set>.md.
    notas = RAIZ / "bench" / ("hallazgos.md" if args.set == "prueba" else f"hallazgos_{args.set}.md")
    texto_hallazgos = notas.read_text(encoding="utf-8").strip() if notas.exists() else f"_(Los escribe el equipo en `{notas.relative_to(RAIZ).as_posix()}`.)_"
    L += ["", "## Hallazgos", "", texto_hallazgos, "",
          "## Limitaciones", "",
          ("- La autoría de este set está en `bench/hallazgos_ciego.md`. Si quien redactó los casos ya conocía las reglas, el número no sustituye a una prueba independiente."
           if args.set == "ciego" else
           "- El banco (80 casos) fue escrito por el mismo equipo que escribió las reglas. Las frases de prueba son distintas de las de desarrollo, pero quien escribe las reglas conoce el estilo de los ataques."),
          "- Los ataques salen de plantillas y son más regulares que los reales." if args.set != "ciego" else
          "- Los casos son inventados y pocos: los porcentajes son indicativos.",
          "- Cada servidor tiene una sola herramienta y la descripción va en el docstring; otras formas de declararla podrían cambiar lo que ve un escáner estático.",
          "- Solo se cuentan las reglas de los escáneres que analizan descripciones de herramientas; los escáneres tienen otras reglas que aquí no aplican.",
          *(["- Muestra pequeña: los porcentajes son indicativos, no estadísticamente concluyentes."] if args.set != "ciego" else []), ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
