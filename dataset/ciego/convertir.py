"""Valida dataset/ciego/casos_ciegos.csv y lo convierte en dataset/casos_ciegos.jsonl.

- Acepta CSV guardado desde Excel (UTF-8 con BOM, separador coma o punto y coma).
- Disfraza automáticamente las envenenadas de la variante "disfrazada".
- Escribe siempre con saltos de línea LF, así la huella SHA-256 es la misma en cualquier sistema.

Uso:  python dataset/ciego/convertir.py
"""
import csv
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
from generar import disfrazar  # noqa: E402

ORIGEN = AQUI / "casos_ciegos.csv"
DESTINO = AQUI.parent / "casos_ciegos.jsonl"
VARIANTES = {"en", "es", "spanglish", "disfrazada"}
TECNICAS = {"ignorar", "ocultar", "secretos", "previa"}
SEMILLA_DISFRAZ = 31


def leer():
    texto = ORIGEN.read_text(encoding="utf-8-sig")
    separador = ";" if texto.splitlines()[0].count(";") > texto.splitlines()[0].count(",") else ","
    return list(csv.DictReader(texto.splitlines(), delimiter=separador))


def validar(filas):
    errores, ids = [], set()
    for n, f in enumerate(filas, start=2):
        f = {k.strip().lower(): (v or "").strip() for k, v in f.items() if k}
        donde = f"fila {n}"
        if not f.get("id"):
            errores.append(f"{donde}: falta el id")
        elif f["id"] in ids:
            errores.append(f"{donde}: el id {f['id']} está repetido")
        ids.add(f.get("id"))
        if f.get("variante") not in VARIANTES:
            errores.append(f"{donde}: variante «{f.get('variante')}» no válida (usa en, es, spanglish o disfrazada)")
        if f.get("envenenada", "").lower() not in {"si", "sí", "no"}:
            errores.append(f"{donde}: envenenada debe ser si o no")
        env = f.get("envenenada", "").lower() in {"si", "sí"}
        tec = f.get("tecnica", "")
        if env and (not tec or not set(tec.split("+")) <= TECNICAS):
            errores.append(f"{donde}: técnica «{tec}» no válida (usa ignorar, ocultar, secretos, previa o dos unidas con +)")
        if not env and tec not in {"", "ninguna"}:
            errores.append(f"{donde}: una limpia lleva tecnica = ninguna")
        if len(f.get("descripcion", "")) < 15:
            errores.append(f"{donde}: la descripción es demasiado corta")
    return errores


def main():
    if not ORIGEN.exists():
        sys.exit(f"No encuentro {ORIGEN}. Escribe los casos ahí primero.")
    filas = leer()
    errores = validar(filas)
    if errores:
        print("Hay que corregir el CSV antes de convertirlo:")
        for e in errores:
            print("  ·", e)
        sys.exit(1)

    rng = random.Random(SEMILLA_DISFRAZ)
    casos = []
    for f in filas:
        f = {k.strip().lower(): (v or "").strip() for k, v in f.items() if k}
        env = f["envenenada"].lower() in {"si", "sí"}
        desc = f["descripcion"]
        if f["variante"] == "disfrazada" and env:
            desc = disfrazar(desc, rng)
        casos.append({"id": f["id"], "variante": f["variante"], "envenenada": env,
                      "tecnica": f.get("tecnica") or "ninguna", "grupo": "ciego", "descripcion": desc})

    with DESTINO.open("w", encoding="utf-8", newline="\n") as fh:
        for c in casos:
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")

    cuenta = Counter((c["variante"], c["envenenada"]) for c in casos)
    print(f"{len(casos)} casos convertidos en {DESTINO.relative_to(AQUI.parent.parent)}")
    print(f"{'variante':<12}{'limpias':>9}{'envenenadas':>13}")
    for v in ["en", "es", "spanglish", "disfrazada"]:
        print(f"{v:<12}{cuenta[(v, False)]:>9}{cuenta[(v, True)]:>13}")
    avisos = [v for v in ["en", "es", "spanglish", "disfrazada"] if cuenta[(v, False)] < 3 or cuenta[(v, True)] < 3]
    if len(casos) < 24 or avisos:
        print("Aviso: lo recomendado es al menos 24 casos y 3 limpias + 3 envenenadas por variante.",
              f"Faltan en: {', '.join(avisos)}" if avisos else "")
    print("SHA-256:", hashlib.sha256(DESTINO.read_bytes()).hexdigest())
    print("Siguiente paso: commit del set ciego ANTES de medir (ver INSTRUCCIONES.md).")


if __name__ == "__main__":
    main()
