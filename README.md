# Escudo MCP en español

Verificador de conectores MCP para agentes de IA. Mide si un ataque escrito en español se le escapa a los detectores que ya existen, y se coloca entre el agente y el conector para que la herramienta envenenada no llegue.

| | |
|---|---|
| Equipo | Arquisoft |
| Evento | AI Security Build Sprint · Cursor Bolivia · 31/10/2026 · UTEPSA |
| Track | 1 · AI Security & AI Safety |
| Qué es | MVP local. No es un producto de producción. |

## Cómo funciona

El agente, igual que Cursor al arrancar, pide la lista de herramientas de un conector MCP y lee cada descripción como si fuera de confianza. Si esa descripción esconde una orden (leer un archivo de claves, no avisarle a la persona, ignorar las instrucciones anteriores), el agente puede cumplirla. Eso se llama tool poisoning.

El Escudo hace cuatro revisiones antes de dejar pasar nada:

1. **Normaliza** el texto: quita caracteres invisibles, convierte letras de otro alfabeto que imitan a las latinas, saca tildes y pasa a minúsculas.
2. **Busca intenciones** en español, inglés y spanglish (ignorar instrucciones, ocultar algo, leer o enviar secretos, dar una orden previa). Cada hallazgo cita la frase que lo disparó.
3. **Revisa el resto de la herramienta:** la descripción de los parámetros, la respuesta que devuelve y una huella SHA-256. Si la herramienta cambia después de haber sido aprobada (rug pull), la siguiente llamada se bloquea.
4. **Mira los argumentos** de la llamada. Si traen algo con forma de secreto, no los reenvía al conector.

Si la herramienta está envenenada, queda en cuarentena: el agente no la ve. Si el escudo no puede analizar el conector, no entrega la lista. Falla cerrado.

```
Agente  →  Escudo verificador :9200  →  Conector :9100
              │
              ├─ limpia  → la deja ver y reenvía la llamada
              └─ envenenada, cambiada o con secreto  → cuarentena, no reenvía
```

El escudo no usa un modelo. Las reglas son explícitas y corren sin clave. Un informe posterior redacta, para el analista, una frase por regla y rechaza un archivo, una URL o una IP que no esté en la descripción.

## Qué ya está medido

Ningún número de aquí se escribe a mano. Salen de `python bench/bench.py`.

| Banco | mcpscan | mcp-audit | Escudo ES | Falsas alarmas del Escudo |
|-------|---------|-----------|-----------|---------------------------|
| Set de prueba, 12 ataques | 5 de 12 | 5 de 12 | 12 de 12 | 0 de 12 |
| 32 paráfrasis, 16 ataques | 3 de 16 | 4 de 16 | 12 de 16 | 0 de 16 |

El 12 de 12 tiene sesgo: la misma persona escribió esas frases y las reglas. Las 32 paráfrasis las redactó alguien que ya había leído las reglas: no son un examen ciego. En español el Escudo vio 1 de 4 paráfrasis. Las que se le fueron son C06, C07, C08 y C15. No se ajustaron las reglas después de verlas.

En el set de desarrollo, con frases típicas, mcp-audit vio 7 de 7 ataques en inglés y 0 de 7 en español.

## Cómo ejecutarlo

Hace falta Python 3.10 o superior. El escudo en sí usa solo la biblioteca estándar. Los escáneres y el laboratorio MCP usan el entorno `.venv-scanners`.

```bash
python -m venv .venv-scanners
.venv-scanners/Scripts/python -m pip install -r requirements-scanners.txt
```

En macOS o Linux el ejecutable está en `.venv-scanners/bin/python`.

**Demo del MVP, un comando.** Levanta el conector de laboratorio en el puerto 9100, el verificador en el 9200 y la web en el 8770. Ctrl+C detiene lo que arrancó.

```bash
python laboratorio/iniciar_demo.py
```

Abrir http://127.0.0.1:8770/laboratorio . Activar el modo guion. Comparar «Escudo ES desactivado» y «Escudo ES activado», y tocar `calcular_iva`.

Otras páginas de la misma web:

| Página | Para qué |
|--------|----------|
| `/` | Simulación: el agente se conecta a 3 conectores, con y sin escudo |
| `/laboratorio` | Línea de tiempo de la demo |
| `/conectores` | Verificar un conector por URL o pegando un `mcp.json` |
| `/escanear` | Pasar una descripción por mcpscan, mcp-audit y el Escudo |

**Reproducir los números**

```bash
python -m unittest escudo.test_escudo escudo.test_informe -v
python bench/bench.py --set prueba
python bench/bench.py --set ciego --out bench/informe_ciego.md
python validar.py
```

`bench.py --set prueba` reescribe `RESULTS.md`. Todo corre en local, con descripciones y claves ficticias. No se escanean servidores MCP de terceros.

## Cómo comprobarlo

Los números de la tabla ya están en el repositorio. Se pueden leer sin volver a instalar los escáneres.

| Qué se comprueba | Dónde está |
|---|---|
| Set de prueba, 12 de 12 | [`RESULTS.md`](RESULTS.md) y [`bench/resultados_prueba.csv`](bench/resultados_prueba.csv) |
| 32 paráfrasis, 12 de 16 | [`bench/informe_ciego.md`](bench/informe_ciego.md) y [`bench/resultados_ciego.csv`](bench/resultados_ciego.csv) |
| Por qué esas paráfrasis no son un examen ciego | [`bench/hallazgos_ciego.md`](bench/hallazgos_ciego.md) |
| Laboratorio: 12 de 12 invariantes | [`VALIDACION.md`](VALIDACION.md), definidas en [`docs/08-logica-principal.md`](docs/08-logica-principal.md) |

El informe de paráfrasis dice la fecha y el SHA-256 del banco. Si alguien vuelve a correr `bench.py --set ciego`, el informe nuevo tiene que coincidir con ese archivo mientras no cambien las reglas ni los casos.

## Demo publicada

https://robydaniel45san.github.io/escudo-mcp-es/

Es la misma pantalla que http://127.0.0.1:8770/laboratorio : línea de tiempo, veredicto y modo guion. Los botones A, B, C y D reproducen las sesiones medidas `A-134840`, `B-134844`, `C-134850` y `D-134855`. En esa página no hay un conector abierto a internet. Para volver a correrlas en vivo, en esta máquina: `python laboratorio/iniciar_demo.py`. Cada push a `main` republica la página con `.github/workflows/pages.yml`.

## Qué no hace

- No promete cubrir cualquier paráfrasis. El hueco en español está medido y listado.
- No entrena un modelo. La página publicada reproduce el registro del laboratorio; el verificador en vivo sigue en esta máquina.
- No lee archivos reales ni envía nada a internet. El «secreto» del laboratorio es el canario `CANARIO-ARQUISOFT-0001`.

## Equipo

Roby Daniel Duran Aguilar · Ronald Augusto Rodriguez Serrano · Ariane Somoza Rocha · Carla Loayza.

## Licencias de lo que ya existía

mcpscan-cli 0.21.0, mcp-audit 0.25.1 y el SDK de MCP en Python se usan sin modificar. El detalle está en `THIRD_PARTY.md`. Lo que aportó el equipo es el banco, las reglas bilingües, el verificador y la medición.
