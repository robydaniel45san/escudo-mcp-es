# demo

## Simulación con conectores MCP (la principal)
```bash
python demo/web.py        # abrir http://127.0.0.1:8765
```
Un agente simulado lee `conectores.json`, se conecta **por MCP de verdad** (stdio) a tres conectores de juguete y recibe sus herramientas. `puerta.py` hace de puerta de entrada: el Escudo ES revisa cada descripción antes de que el agente la vea.

| Conector | Herramientas | Qué tiene |
|----------|--------------|-----------|
| `tienda` | `calcular_iva`, `convertir_moneda` | `calcular_iva` esconde una orden en spanglish |
| `clima` | `clima_actual`, `pronostico` | Todo limpio |
| `archivos` | `listar_archivos`, `buscar_texto` | `buscar_texto` esconde una orden disfrazada con letras cirílicas y un carácter invisible |

- **Con escudo:** el agente ve 4 herramientas; 2 quedan en cuarentena con su frase culpable.
- **Sin escudo:** el agente ve las 6 y el log muestra 6 acciones dañinas **simuladas** (no se lee ni se envía ningún archivo).

Cada corrida se guarda en `demo/logs/escudo-AAAAMMDD-HHMMSS.jsonl` (fuera del repositorio).

En la terminal, el mismo log con colores:
```bash
.venv-scanners/Scripts/python demo/puerta.py
.venv-scanners/Scripts/python demo/puerta.py --sin-escudo
```

## Escanear una descripción
La pestaña "Escanear una descripción" (`/escanear`) corre mcpscan, mcp-audit y el Escudo ES sobre un texto, y muestra la tabla del set de prueba.

## Archivos
- `conectores/`, `conectores.json`: conectores MCP de juguete y su configuración, con el formato de `mcp.json`.
- `puerta.py`: cliente MCP real + Escudo ES + log.
- `web.py`, `web/`: servidor local (solo biblioteca estándar) y las dos páginas.
- `demo.py`, `servidor_iva.py`: demo de terminal (respaldo).

Requiere `.venv-scanners` (ver el README principal): tiene el SDK de MCP y los escáneres.
