# 08 · Lógica principal del Escudo MCP

## La idea en una frase
**Ninguna instrucción escondida en un conector MCP debe llegar al agente, ni ningún secreto debe salir de él, aunque el ataque esté en español, disfrazado o cambie después de aprobado.**

## El recorrido de una herramienta por el escudo

```
Conector MCP ──► 1. Recibir la definición (tools/list)
                    │
                    ▼
                 2. Normalizar el texto ── quita invisibles, homoglifos y tildes
                    │
                    ▼
                 3. Buscar intenciones ─── reglas en inglés y español sobre
                    │                       la descripción y el esquema completo
                    ▼
                 4. ¿Envenenada? ── sí ──► CUARENTENA (el agente no la ve)
                    │ no
                    ▼
                 5. Huella SHA-256 de la definición aprobada
                    │
                    ▼
Agente ◄──────── 6. Lista solo con herramientas limpias
   │
   └─ llama ───► 7. ¿Cambió la definición? ── sí ──► CUARENTENA (rug pull)
                 8. ¿Los argumentos llevan un secreto? ── sí ──► BLOQUEO (exfiltración)
                 9. Reenviar al conector
                10. ¿La respuesta trae órdenes? ── sí ──► RETENER la respuesta
Agente ◄────────11. Respuesta revisada
                12. Cada paso queda en el registro estandarizado (OpenTelemetry + OCSF)
```

**Fallar cerrado:** si el escudo no puede hablar con el conector o no puede analizar, el agente **no** recibe herramientas sin revisar.

## Invariantes: lo que nunca se puede romper

| # | Invariante | Cómo se comprueba (`validar.py`) | Requisito / rúbrica |
|---|------------|----------------------------------|---------------------|
| I1 | El texto disfrazado se normaliza (homoglifos, invisibles, tildes) | Tests de `escudo/` | REQ-05 · R2 |
| I2 | Las reglas detectan la intención en inglés, español y spanglish, sin falsas alarmas en el set de desarrollo | Tests de `escudo/` y del informe | REQ-06 · R1 |
| I3 | El set de prueba está congelado y no cambió | Huella SHA-256 = `dc2c207e…` | REQ-03 · R3 |
| I4 | La medición es reproducible: el mismo comando da los mismos resultados | Se corre `bench.py --set prueba` y se compara con el CSV guardado | REQ-10 · R3 |
| I5 | El hallazgo se sostiene: los escáneres existentes detectan menos que con el escudo | Lectura del CSV oficial | REQ-07 · R1 |
| I6 | Sin escudo, un agente obediente filtra el secreto (el ataque es real) | Escenario A: el canario sale | REQ-04 · R3 |
| I7 | Con escudo, ninguna herramienta envenenada (descripción o esquema) llega al agente | Escenario B: cuarentenas y 0 robos | REQ-04 · R1 |
| I8 | Un cambio de definición después de aprobada se bloquea | Escenario C: rug pull detectado | R1 |
| I9 | Una respuesta envenenada no llega al agente | Escenario D: respuesta retenida | R1 |
| I10 | Un argumento con forma de secreto no sale | Escenario B: exfiltración bloqueada | MCP01 · R1 |
| I11 | El escudo falla cerrado si el conector no responde | Verificador apuntando a un conector caído: la lista devuelve error, no herramientas | R2 |
| I12 | Cada sesión queda en el registro estándar, con el punto clave marcado y sin argumentos completos | Lectura de `eventos.jsonl` | REQ-09 · R3 |
| I13 | El repositorio no contiene claves, `.env` reales ni logs | Revisión de los archivos versionados | REQ-13 · REG-2 |

## Cómo validar todo
```bash
python validar.py            # validación completa (unos 2 minutos), escribe VALIDACION.md
python validar.py --rapida   # sin volver a medir con los escáneres
```
El validador usa los servicios del laboratorio si ya están corriendo (`iniciar_demo.py`) y, si no, los levanta solo.
