# Contribución (entregable C)

## Qué existía antes del desarrollo
| Elemento | Origen | Uso en el proyecto |
|----------|--------|--------------------|
| Documentación (`docs/`, README, plantillas) | Equipo, commit `4f98b59` | Plan, pitch y trazabilidad |
| Idea de las reglas del escudo | Equipo: un prototipo de demostración en la web de estudio Misión Sprint (laboratorio T1-07, 13 casos) | Punto de partida conceptual; el código de `escudo/` se reescribió desde cero en Python |
| mcpscan-cli 0.21.0 y mcp-audit 0.25.1 | Terceros, ver `THIRD_PARTY.md` | Línea base, sin modificar |
| SDK de MCP en Python 1.30.0 | Terceros | Servidores de juguete |
| Entorno preparado y prueba de humo con **un solo caso en inglés** | Equipo | Confirmar que la línea base corre en local |

## Qué hicimos durante el sprint
Inicio del desarrollo: 31/10/2026, ~10:20 (después del commit de material previo) · Hora oficial de inicio: _(completar)_

| Componente | Descripción |
|------------|-------------|
| `dataset/generar.py` | Banco reproducible de 80 descripciones MCP ficticias en 4 variantes (inglés, español, spanglish, disfrazada), con limpias difíciles y frases de ataque separadas entre desarrollo y prueba |
| `dataset/casos_prueba.jsonl` | Set de prueba de 24 casos, congelado a las 10:24 con su huella SHA-256, antes de escribir las reglas |
| `escudo/` | Normalización (invisibles, homoglifos, tildes), detección de palabras con alfabetos mezclados y 8 reglas bilingües de intención con frase culpable |
| `escudo/test_escudo.py` | 13 tests (normalización, reglas y set de desarrollo completo) |
| `bench/bench.py` | Genera un servidor MCP por caso, corre mcpscan y mcp-audit `--connect`, aplica el escudo y escribe `RESULTS.md` y un CSV |
| `demo/` | Servidor MCP de juguete con una herramienta envenenada en spanglish y demo de línea de comandos |
| `escudo/informe.py` | Informe del hallazgo: cita la frase de cada regla, junta las alertas de la misma descripción en un incidente y rechaza archivos, URLs o IPs que no están en el texto |

## Pruebas reproducibles
```bash
python -m unittest escudo.test_escudo escudo.test_informe -v
python bench/bench.py --set prueba
python demo/demo.py
```

## Resultado principal (set de prueba)
Ver [`RESULTS.md`](RESULTS.md). Los escáneres existentes detectaron 5 de 12 ataques; con el Escudo ES se detectaron 12 de 12, sin falsas alarmas nuevas. **Ese 12 de 12 tiene un sesgo declarado:** la misma persona escribió las frases de prueba y las reglas. Falta validarlo con un set ciego.

## Origen de los datos
Todos los casos son ficticios y los generó el equipo. Ver `DATASET.md`.
