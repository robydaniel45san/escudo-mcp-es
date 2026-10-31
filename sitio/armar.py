"""Arma el sitio público con la misma pantalla que http://127.0.0.1:8770/laboratorio.

Los escenarios A–D reproducen las sesiones ya medidas. En la máquina local esos
botones vuelven a correr el laboratorio; aquí no hay conector ni escudo en internet.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = Path(sys.argv[1] if len(sys.argv) > 1 else RAIZ / "_site")

html = (RAIZ / "demo" / "web" / "laboratorio.html").read_text(encoding="utf-8")
html = html.replace('src="/alertas.js"', 'src="alertas.js"')
html = html.replace('href="/laboratorio"', 'href="index.html"')
html = html.replace('href="/conectores"', 'href="index.html#conectores"')
html = html.replace('href="/escanear"', 'href="index.html#escanear"')
html = html.replace('href="/"', 'href="index.html#simulacion"')
html = html.replace(
    '<script src="alertas.js"></script>',
    '<script src="lab.js"></script>\n<script src="alertas.js"></script>',
)
nota = (
    '<script>addEventListener("hashchange",aviso);addEventListener("DOMContentLoaded",aviso);'
    'function aviso(){const e=document.querySelector("#err");if(!e)return;'
    'const mapa={"#simulacion":"/","#conectores":"/conectores","#escanear":"/escanear"};'
    'if(!mapa[location.hash]){return}'
    'e.hidden=false;e.textContent="Esa pantalla está en la demo local: http://127.0.0.1:8770"+mapa[location.hash];}'
    '</script>'
)
html = html.replace("</body>", nota + "\n</body>")

DESTINO.mkdir(parents=True, exist_ok=True)
(DESTINO / "index.html").write_text(html, encoding="utf-8")
(DESTINO / "alertas.js").write_bytes((RAIZ / "demo" / "web" / "alertas.js").read_bytes())
(DESTINO / "lab.js").write_bytes((Path(__file__).parent / "lab.js").read_bytes())
(DESTINO / ".nojekyll").write_text("", encoding="utf-8")
print(DESTINO)
