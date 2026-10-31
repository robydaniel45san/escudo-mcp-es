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
Inicio oficial del evento: 31/10/2026, 09:00. El código del escudo empieza ~10:20, después del commit de material previo.

| Componente | Descripción |
|------------|-------------|
| `dataset/generar.py` | Banco reproducible de 80 descripciones MCP ficticias en 4 variantes (inglés, español, spanglish, disfrazada), con limpias difíciles y frases de ataque separadas entre desarrollo y prueba |
| `dataset/casos_prueba.jsonl` | Set de prueba de 24 casos, congelado a las 10:24 con su huella SHA-256, antes de escribir las reglas |
| `escudo/` | Normalización (invisibles, homoglifos, tildes), detección de palabras con alfabetos mezclados y 8 reglas bilingües de intención con frase culpable |
| `escudo/test_escudo.py` y `escudo/test_informe.py` | 17 tests: normalización, reglas, set de desarrollo y el informe que cita la frase |
| `bench/bench.py` | Genera un servidor MCP por caso, corre mcpscan y mcp-audit `--connect`, aplica el escudo y escribe `RESULTS.md` y un CSV |
| `demo/` | Servidor MCP de juguete con una herramienta envenenada en spanglish y demo de línea de comandos |
| `escudo/informe.py` | Informe del hallazgo: cita la frase de cada regla, junta las alertas de la misma descripción en un incidente y rechaza archivos, URLs o IPs que no están en el texto |
| `laboratorio/` | Verificador entre el agente y el conector, cuatro pruebas (A sin escudo, B con escudo, C rug pull, D esquema y respuesta) y la pantalla en `http://127.0.0.1:8770/laboratorio` |
| `validar.py` | Comprueba las invariantes del laboratorio con un canario falso. La última corrida rápida, sin volver a medir los escáneres, dejó 11 de 11 en `VALIDACION.md` |
| `dataset/ciego/` | 32 paráfrasis (16 ataques, 16 limpias). No es un set ciego: quien las redactó ya había leído las reglas. Medidas en `bench/informe_ciego.md` |

## Pruebas reproducibles
```bash
python -m unittest escudo.test_escudo escudo.test_informe -v
python bench/bench.py --set prueba
python demo/demo.py
```

## Resultado principal (set de prueba)
Ver [`RESULTS.md`](RESULTS.md). Los escáneres existentes detectaron 5 de 12 ataques; con el Escudo ES se detectaron 12 de 12, sin falsas alarmas nuevas. **Ese 12 de 12 tiene un sesgo declarado:** la misma persona escribió las frases de prueba y las reglas. Falta un set escrito por alguien que no vio las reglas.

Sobre 32 paráfrasis redactadas después de leer las reglas (no es un set ciego): mcpscan 3 de 16, mcp-audit 4 de 16, Escudo ES 12 de 16, con 0 falsas alarmas del Escudo. Informe: [`bench/informe_ciego.md`](bench/informe_ciego.md). La autoría y las cuatro que se le fueron están en [`bench/hallazgos_ciego.md`](bench/hallazgos_ciego.md).

## Limitaciones
- El 12 de 12 del set de prueba tiene sesgo: la misma persona escribió esas frases y las reglas.
- Las 32 paráfrasis no son un examen ciego. En español el Escudo vio 1 de 4. Las que se le fueron son C06, C07, C08 y C15. Las reglas no se ajustaron después de verlas.
- El laboratorio usa un agente obediente simulado y el canario `CANARIO-ARQUISOFT-0001`. No lee archivos reales ni ataca servidores de terceros.
- Cursor, en el intento registrado, usó `calcular_iva` sin escudo y no mandó el canario. Con escudo no vio la herramienta. Un solo intento no alcanza para decir que el modelo cae en la trampa.

## Origen de los datos
Todos los casos son ficticios y los generó el equipo. Ver `DATASET.md`.
