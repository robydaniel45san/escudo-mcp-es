"""Muestra en vivo los logs del laboratorio: lo que recibe el atacante y lo que bloquea el escudo.

Uso:  python laboratorio/ver_logs.py            (Ctrl+C para salir)
      python laboratorio/ver_logs.py --resumen  (solo el conteo final)
"""
import json
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
LOGS = {"ATACANTE": AQUI / "logs" / "atacante.jsonl", "ESCUDO": AQUI / "logs" / "verificador.jsonl"}
ROJO, AMARILLO, VERDE, GRIS, NEGRITA, FIN = "\033[31m", "\033[33m", "\033[32m", "\033[90m", "\033[1m", "\033[0m"


def formato(origen, r):
    hora = r.get("t", "")[11:19]
    if origen == "ATACANTE":
        if r.get("canario_capturado"):
            return f"{hora} {ROJO}{NEGRITA}ATACANTE  ⚠ CANARIO CAPTURADO{FIN} en {r.get('herramienta')}: {str(r.get('notas') or r.get('moneda') or r.get('ciudad'))[:80]}"
        if r.get("evento") == "rug_pull":
            return f"{hora} {AMARILLO}ATACANTE  cambió la descripción de {r.get('herramienta')} (rug pull){FIN}"
        if r.get("evento") == "llamada":
            return f"{hora} {GRIS}ATACANTE  recibió una llamada a {r.get('herramienta')}{FIN}"
        return f"{hora} {GRIS}ATACANTE  {r.get('evento')}{FIN}"
    color = {"OK": VERDE, "BLOQUEO": AMARILLO, "ALERTA": ROJO}.get(r.get("nivel"), GRIS)
    return f"{hora} {color}ESCUDO    {r.get('nivel', ''):<8}{FIN} {r.get('mensaje', '')}"


def leer_nuevas(posiciones):
    lineas = []
    for origen, ruta in LOGS.items():
        if not ruta.exists():
            continue
        with ruta.open(encoding="utf-8") as f:
            f.seek(posiciones.get(origen, 0))
            while True:
                inicio = f.tell()
                linea = f.readline()
                if not linea:
                    break
                if not linea.endswith("\n"):
                    f.seek(inicio)
                    break
                if not linea.strip():
                    continue
                try:
                    r = json.loads(linea)
                except json.JSONDecodeError:
                    continue
                lineas.append((r.get("t", ""), origen, r))
            posiciones[origen] = f.tell()
    return sorted(lineas, key=lambda x: x[0])


def resumen():
    capturas = bloqueos = rug = 0
    for origen, ruta in LOGS.items():
        if not ruta.exists():
            continue
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            if not linea.strip():
                continue
            try:
                r = json.loads(linea)
            except json.JSONDecodeError:
                continue
            capturas += origen == "ATACANTE" and bool(r.get("canario_capturado"))
            bloqueos += origen == "ESCUDO" and r.get("nivel") in ("BLOQUEO", "ALERTA")
            rug += origen == "ESCUDO" and r.get("tipo") == "rug_pull"
    print(f"Canario capturado por el atacante: {capturas} · Bloqueos del escudo: {bloqueos} · Rug pulls detectados: {rug}")


def main():
    if sys.platform == "win32":
        import os
        os.system("")
        sys.stdout.reconfigure(encoding="utf-8")
    if "--resumen" in sys.argv:
        return resumen()
    print(f"{NEGRITA}Logs del laboratorio en vivo{FIN} {GRIS}(Ctrl+C para salir){FIN}")
    posiciones = {}
    try:
        while True:
            for _, origen, r in leer_nuevas(posiciones):
                print(formato(origen, r), flush=True)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print()
        resumen()


if __name__ == "__main__":
    main()
