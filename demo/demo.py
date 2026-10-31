"""Demo del pitch: escáneres existentes frente al Escudo ES sobre el servidor de juguete.

Uso:
  python demo/demo.py                      # escanea demo/servidor_iva.py
  python demo/demo.py "texto a analizar"   # analiza una descripción suelta con el Escudo ES
"""
import ast
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from escudo import analizar  # noqa: E402
from escudo.informe import redactar  # noqa: E402

SCRIPTS = RAIZ / ".venv-scanners" / ("Scripts" if sys.platform == "win32" else "bin")
EXE = ".exe" if sys.platform == "win32" else ""
SERVIDOR = RAIZ / "demo" / "servidor_iva.py"

ROJO, VERDE, AMARILLO, GRIS, NEGRITA, FIN = "\033[31m", "\033[32m", "\033[33m", "\033[90m", "\033[1m", "\033[0m"


def titulo(texto):
    print(f"\n{NEGRITA}{texto}{FIN}")


def veredicto(envenenada):
    return f"{ROJO}{NEGRITA}ENVENENADA{FIN}" if envenenada else f"{VERDE}{NEGRITA}LIMPIA{FIN}"


def herramientas(ruta):
    """Lee nombre y descripción de cada herramienta del servidor sin ejecutarlo."""
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    return [(n.name, ast.get_docstring(n) or "") for n in arbol.body if isinstance(n, ast.FunctionDef)]


def visible(texto):
    """Marca caracteres invisibles para que se vean en pantalla."""
    return texto.replace("​", f"{AMARILLO}⟦invisible⟧{FIN}")


def resaltar(normalizado, hallazgos):
    for h in hallazgos:
        if h["frase"] in normalizado:
            normalizado = normalizado.replace(h["frase"], f"{ROJO}{NEGRITA}{h['frase']}{FIN}")
    return normalizado


def mcpscan(ruta):
    r = subprocess.run([str(SCRIPTS / f"mcpscan{EXE}"), "--json", "--min-severity", "critical", str(ruta)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    return [f for f in json.loads(r.stdout).get("findings", []) if f.get("rule_id") in {"MCP002", "MCP023"}]


def mcpaudit(ruta):
    with tempfile.TemporaryDirectory() as tmp:
        config = Path(tmp) / "mcp.json"
        py = SCRIPTS / f"python{EXE}"
        config.write_text(json.dumps({"mcpServers": {"tienda_demo": {"command": str(py), "args": [str(ruta)]}}}), encoding="utf-8")
        r = subprocess.run([str(SCRIPTS / f"mcp-audit{EXE}"), "scan", str(config), "--connect", "--format", "json"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    datos = json.loads(r.stdout[r.stdout.find("{"):])
    return [f for f in datos.get("findings", []) if f.get("analyzer") in {"poisoning", "delegation"}]


def mostrar_escudo(descripcion):
    res = analizar(descripcion)
    print(f"  {GRIS}Lo que ve una persona:{FIN}     {visible(descripcion)}")
    print(f"  {GRIS}Lo que analiza el escudo:{FIN}  {resaltar(res['normalizado'], res['hallazgos'])}")
    print(f"  Escudo ES → {veredicto(res['envenenada'])}")
    for h in res["hallazgos"]:
        print(f"    · {h['regla']}: \"{h['frase']}\"")
    informe = redactar(descripcion, res)
    if informe["afirmaciones"]:
        print(f"  {GRIS}Informe ({informe['respaldadas']}/{informe['total']} afirmaciones respaldadas):{FIN}")
        for a in informe["afirmaciones"]:
            marca = f"{VERDE}respaldada{FIN}" if a["respaldada"] else f"{ROJO}rechazada{FIN}"
            print(f"    · [{marca}] {a['texto']}")
        ajenos = ", ".join(informe["sin_citas"]["inventados"])
        print(f"  {GRIS}Resumen sin citas, rechazado ({ajenos}):{FIN} {informe['sin_citas']['texto']}")
    return res


def main():
    if len(sys.argv) > 1:
        titulo("Escudo ES")
        mostrar_escudo(" ".join(sys.argv[1:]))
        return

    titulo(f"Servidor MCP de juguete: {SERVIDOR.name}")
    for nombre, desc in herramientas(SERVIDOR):
        print(f"  · {nombre}: {desc.splitlines()[0]}")

    titulo("1 · Escáneres existentes (sin modificar)")
    hs = mcpscan(SERVIDOR)
    print(f"  mcpscan 0.21.0   → {veredicto(bool(hs))}" + "".join(f"\n    · {h['rule_id']}: {h['snippet']}" for h in hs))
    print(f"  {GRIS}(levantando el servidor para mcp-audit…){FIN}", end="\r")
    ha = mcpaudit(SERVIDOR)
    print(f"  mcp-audit 0.25.1 → {veredicto(bool(ha))}" + "".join(f"\n    · {h['title']} ({h['evidence']})" for h in ha) + " " * 20)

    titulo("2 · Escudo ES (normalización + reglas bilingües)")
    for nombre, desc in herramientas(SERVIDOR):
        print(f"\n  {NEGRITA}{nombre}{FIN}")
        mostrar_escudo(" ".join(desc.split()))

    titulo("Resultados medidos sobre el banco: ver RESULTS.md")


if __name__ == "__main__":
    if sys.platform == "win32":
        import os
        os.system("")  # activa los colores ANSI en la consola de Windows
        sys.stdout.reconfigure(encoding="utf-8")
    main()
