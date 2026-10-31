"""Valida que el proyecto cumpla la lógica principal (docs/08-logica-principal.md).

Cada invariante es una prueba real: tests, huella del set congelado, medición repetida,
escenarios del laboratorio, fallo cerrado del verificador, registro estandarizado y
revisión del repositorio. Escribe el resultado en VALIDACION.md.

Uso (desde la carpeta escudo-mcp-es):
  python validar.py            # completa (unos 2 minutos)
  python validar.py --rapida   # sin volver a medir con los escáneres (I4)
"""
import csv
import datetime as dt
import json
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
WIN = sys.platform == "win32"
PY_VENV = RAIZ / ".venv-scanners" / ("Scripts" if WIN else "bin") / ("python.exe" if WIN else "python")
HUELLA_PRUEBA = "dc2c207ecc4354a004e77f392d30eecf4385870b6d8fd6b389f45a6711fd5ba7"
sys.path.insert(0, str(RAIZ / "laboratorio"))
import eventos  # noqa: E402

resultados = []


def invariante(codigo, nombre):
    def deco(fn):
        def correr():
            inicio = time.time()
            try:
                ok, detalle = fn()
            except Exception as e:  # una prueba que falla con error cuenta como falla
                ok, detalle = False, f"error: {e}"
            resultados.append((codigo, nombre, ok, detalle, time.time() - inicio))
            marca = "\033[32m✓\033[0m" if ok else "\033[31m✗\033[0m"
            print(f"{marca} {codigo} {nombre}\n    {detalle}", flush=True)
        correr.codigo = codigo
        return correr
    return deco


def py_venv(*args, timeout=240):
    return subprocess.run([str(PY_VENV), "-X", "utf8", *args], cwd=str(RAIZ), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def puerto_abierto(p):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", p)) == 0


# ---------------------------------------------------------------- I1 · I2
@invariante("I1–I2", "Normalización y reglas bilingües (tests)")
def tests():
    r = subprocess.run([sys.executable, "-X", "utf8", "-m", "unittest", "escudo.test_escudo", "escudo.test_informe"],
                       cwd=str(RAIZ), capture_output=True, text=True, encoding="utf-8", errors="replace")
    total = re.search(r"Ran (\d+) tests", r.stderr)
    return r.returncode == 0, f"{total.group(1) if total else '?'} tests · {'todos pasan' if r.returncode == 0 else r.stderr.strip().splitlines()[-1]}"


# ---------------------------------------------------------------- I3
@invariante("I3", "Set de prueba congelado sin cambios")
def huella():
    import hashlib
    h = hashlib.sha256((RAIZ / "dataset" / "casos_prueba.jsonl").read_bytes()).hexdigest()
    return h == HUELLA_PRUEBA, f"SHA-256 {h[:16]}… {'coincide' if h == HUELLA_PRUEBA else 'NO coincide con ' + HUELLA_PRUEBA[:16]}"


# ---------------------------------------------------------------- I4
@invariante("I4", "Medición reproducible (bench --set prueba)")
def reproducible():
    oficial = RAIZ / "bench" / "resultados_prueba.csv"
    respaldo = Path(tempfile.mkdtemp()) / "oficial.csv"
    shutil.copy(oficial, respaldo)
    try:
        r = subprocess.run([sys.executable, "-X", "utf8", "bench/bench.py", "--set", "prueba", "--out", str(respaldo.parent / "R.md")],
                           cwd=str(RAIZ), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
        if r.returncode != 0:
            return False, "bench.py falló: " + (r.stderr.strip().splitlines() or ["sin detalle"])[-1]
        antes = list(csv.DictReader(respaldo.read_text(encoding="utf-8").splitlines()))
        despues = list(csv.DictReader(oficial.read_text(encoding="utf-8").splitlines()))
        cols = ["id", "mcpscan", "mcpaudit", "escudo"]
        dif = [a["id"] for a, b in zip(antes, despues) if any(a[c] != b[c] for c in cols)]
        return not dif and len(antes) == len(despues), (f"{len(despues)} casos medidos de nuevo · decisiones idénticas" if not dif
                                                        else f"cambian {len(dif)} casos: {', '.join(dif[:5])}")
    finally:
        shutil.copy(respaldo, oficial)   # el validador no modifica los resultados oficiales


# ---------------------------------------------------------------- I5
@invariante("I5", "El hallazgo se sostiene (escáneres < escudo, y el español queda fuera)")
def hallazgo():
    def contar(archivo, col, variante=None):
        filas = [f for f in csv.DictReader((RAIZ / "bench" / archivo).read_text(encoding="utf-8").splitlines())
                 if f["envenenada"] == "True" and (variante is None or f["variante"] == variante)]
        return sum(f[col] == "True" for f in filas), len(filas)
    scan, n = contar("resultados_prueba.csv", "mcpscan")
    audit, _ = contar("resultados_prueba.csv", "mcpaudit")
    esc, _ = contar("resultados_prueba.csv", "escudo")
    es_audit, n_es = contar("resultados_desarrollo.csv", "mcpaudit", "es")
    en_audit, n_en = contar("resultados_desarrollo.csv", "mcpaudit", "en")
    ok = max(scan, audit) < esc and es_audit < en_audit
    return ok, (f"prueba: mcpscan {scan}/{n} · mcp-audit {audit}/{n} · escudo {esc}/{n} — "
                f"desarrollo, mcp-audit: inglés {en_audit}/{n_en} frente a español {es_audit}/{n_es}")


# ---------------------------------------------------------------- I6 a I10
ESCENARIOS = {}


def correr_escenario(clave):
    if clave not in ESCENARIOS:
        r = py_venv("laboratorio/prueba_automatica.py", "--escenario", clave)
        if r.returncode != 0:
            raise RuntimeError(f"el escenario {clave} falló: " + (r.stderr.strip().splitlines() or ["sin detalle"])[-1])
        sesion = eventos.sesion_actual()["sesion"]
        ESCENARIOS[clave] = (sesion, eventos.leer(sesion))
    return ESCENARIOS[clave]


def hay(evs, evento, **campos):
    return [e for e in evs if e.get("evento") == evento and all(e.get(k) == v for k, v in campos.items())]


@invariante("I6", "Sin escudo, el ataque es real: un agente obediente filtra el canario")
def sin_escudo():
    sesion, evs = correr_escenario("A")
    capturas = hay(evs, "conector.captura")
    vias = sorted({e.get("detalle", {}).get("via") for e in hay(evs, "agente.obedece")} - {None})
    return len(capturas) >= 1, f"sesión {sesion}: {len(capturas)} capturas del canario · vías seguidas por el agente: {', '.join(vias)}"


@invariante("I7", "Con escudo, ninguna herramienta envenenada llega al agente")
def con_escudo():
    sesion, evs = correr_escenario("B")
    cuarentenas = {e.get("gen_ai.tool.name") for e in hay(evs, "escudo.cuarentena")}
    capturas = hay(evs, "conector.captura")
    vistas = set()
    for e in hay(evs, "agente.lista_recibida"):
        vistas |= set(e.get("detalle", {}).get("herramientas", []))
    filtradas = cuarentenas & vistas
    ok = {"calcular_iva", "convertir_unidades"} <= cuarentenas and not capturas and not filtradas
    return ok, f"sesión {sesion}: en cuarentena {sorted(cuarentenas)} · el agente vio {sorted(vistas)} · capturas {len(capturas)}"


@invariante("I8", "Un rug pull se bloquea")
def rug_pull():
    sesion, evs = correr_escenario("C")
    rp = hay(evs, "escudo.rug_pull")
    return bool(rp) and not hay(evs, "conector.captura"), f"sesión {sesion}: {len(rp)} rug pull detectado · capturas {len(hay(evs, 'conector.captura'))}"


@invariante("I9", "Una respuesta envenenada no llega al agente")
def respuesta():
    sesion, evs = correr_escenario("D")
    ret = hay(evs, "escudo.salida_bloqueada")
    return bool(ret) and not hay(evs, "conector.captura"), f"sesión {sesion}: {len(ret)} respuesta retenida · capturas {len(hay(evs, 'conector.captura'))}"


@invariante("I10", "Un argumento con forma de secreto no sale")
def exfiltracion():
    sesion, evs = correr_escenario("B")
    bloq = hay(evs, "escudo.exfiltracion_bloqueada")
    llegaron = [e for e in evs if e.get("componente") == "conector" and e.get("gen_ai.tool.call.arguments", {}).get("contiene_canario")]
    return bool(bloq) and not llegaron, f"sesión {sesion}: {len(bloq)} intento bloqueado · argumentos con canario que llegaron al conector: {len(llegaron)}"


# ---------------------------------------------------------------- I11
CLIENTE = """
import asyncio, sys
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
async def main():
    async with streamablehttp_client("http://127.0.0.1:9299/mcp") as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            try:
                lista = await s.list_tools()
                print("HERRAMIENTAS", [t.name for t in lista.tools])
            except Exception as e:
                print("RECHAZO", type(e).__name__)
asyncio.run(main())
"""


@invariante("I11", "El escudo falla cerrado si el conector no responde")
def fallo_cerrado():
    if puerto_abierto(9299):
        return False, "el puerto 9299 está ocupado; no se puede montar la prueba"
    eventos.nueva_sesion(f"Validacion-fallo-cerrado-{dt.datetime.now():%H%M%S}")
    p = subprocess.Popen([str(PY_VENV), "laboratorio/verificador.py", "--conector", "http://127.0.0.1:9599/mcp", "--puerto", "9299"],
                         cwd=str(RAIZ), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            if puerto_abierto(9299):
                break
            time.sleep(0.25)
        r = py_venv("-c", CLIENTE, timeout=60)
        salida = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr.strip()[-120:]
        ok = salida.startswith("RECHAZO") or (r.returncode != 0 and "HERRAMIENTAS" not in r.stdout)
        return ok, ("el agente recibe un error y ninguna herramienta sin revisar" if ok else f"respuesta inesperada: {salida}")
    finally:
        p.terminate()
        p.wait(timeout=10)


# ---------------------------------------------------------------- I12
@invariante("I12", "Registro estandarizado: sesiones, punto clave y argumentos recortados")
def registro():
    if not ESCENARIOS:
        return False, "no se corrieron escenarios"
    problemas = []
    for clave, (sesion, evs) in ESCENARIOS.items():
        if len({e["trace_id"] for e in evs}) != 1:
            problemas.append(f"{clave}: más de un trace_id")
        q, d = eventos.puntos_clave(evs)
        if not (q or d):
            problemas.append(f"{clave}: sin punto de quiebre ni de defensa")
        for e in evs:
            a = e.get("gen_ai.tool.call.arguments")
            if a and (set(a) - {"vista", "contiene_canario"} or len(a.get("vista", "")) > 121):
                problemas.append(f"{clave}: argumentos guardados completos")
            for campo in ("@timestamp", "span.name", "severity_id", "componente", "evento"):
                if campo not in e:
                    problemas.append(f"{clave}: falta {campo}")
                    break
    total = sum(len(evs) for _, evs in ESCENARIOS.values())
    return not problemas, (f"{total} eventos en {len(ESCENARIOS)} sesiones · un trace_id por sesión · punto clave en todas · argumentos recortados"
                           if not problemas else "; ".join(sorted(set(problemas))[:4]))


# ---------------------------------------------------------------- I13
@invariante("I13", "El repositorio no contiene claves, .env reales ni logs")
def repositorio():
    archivos = subprocess.run(["git", "ls-files"], cwd=str(RAIZ), capture_output=True, text=True).stdout.splitlines()
    malos = [a for a in archivos if re.search(r"(^|/)\.env$|\.pem$|\.key$|(^|/)logs(-[^/]*)?/|\.venv", a)]
    clave = re.compile(r"sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{30,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----")
    con_clave = [a for a in archivos if (RAIZ / a).is_file() and (RAIZ / a).stat().st_size < 2_000_000
                 and clave.search((RAIZ / a).read_text(encoding="utf-8", errors="ignore"))]
    ok = not malos and not con_clave
    return ok, f"{len(archivos)} archivos versionados · " + ("sin claves, .env ni logs" if ok else f"revisar: {', '.join((malos + con_clave)[:5])}")


def informe():
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(RAIZ), capture_output=True, text=True).stdout.strip()
    pasan = sum(r[2] for r in resultados)
    lineas = ["# Validación de la lógica principal", "",
              f"> Generado por `python validar.py{' --rapida' if '--rapida' in sys.argv else ''}` el {dt.datetime.now():%Y-%m-%d %H:%M} sobre el commit `{commit}`. "
              "Las invariantes están definidas en [`docs/08-logica-principal.md`](docs/08-logica-principal.md).", "",
              f"**Resultado: {pasan} de {len(resultados)} invariantes se cumplen.**", "",
              "| Invariante | Qué se comprueba | Resultado | Detalle |", "|---|---|---|---|"]
    for codigo, nombre, ok, detalle, _ in resultados:
        lineas.append(f"| {codigo} | {nombre} | {'✅ cumple' if ok else '❌ falla'} | {detalle.replace('|', '/')} |")
    lineas += ["", "Las pruebas de I6 a I12 usan el laboratorio local (conector malicioso :9100 y Escudo verificador :9200) "
               "con un agente obediente simulado y un canario falso. Ningún dato es real.", ""]
    (RAIZ / "VALIDACION.md").write_text("\n".join(lineas), encoding="utf-8")
    return pasan


def main():
    if WIN:
        import os
        os.system("")
        sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    if not PY_VENV.exists():
        sys.exit("Falta .venv-scanners. Ver el README: python -m venv .venv-scanners y pip install -r requirements-scanners.txt")
    print("Escudo MCP · validación de la lógica principal\n")
    pruebas = [tests, huella] + ([] if "--rapida" in sys.argv else [reproducible]) + \
              [hallazgo, sin_escudo, con_escudo, rug_pull, respuesta, exfiltracion, fallo_cerrado, registro, repositorio]
    for p in pruebas:
        p()
    pasan = informe()
    print(f"\n{pasan} de {len(resultados)} invariantes se cumplen · informe en VALIDACION.md")
    sys.exit(0 if pasan == len(resultados) else 1)


if __name__ == "__main__":
    main()
