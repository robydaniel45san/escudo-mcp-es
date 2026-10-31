# Resultados

> Generado por `bench/bench.py --set prueba` el 2026-10-31 10:29. Ningún número se escribe a mano.

- Banco: `dataset/casos_prueba.jsonl` · 24 casos · SHA-256 `dc2c207ecc4354a004e77f392d30eecf4385870b6d8fd6b389f45a6711fd5ba7`
- mcpscan: 24 archivos analizados · reglas contadas: MCP002, MCP023
- mcp-audit `--connect`: 24 servidores conectados · analizadores contados: delegation, poisoning
- Escudo ES: normalización + reglas bilingües (`escudo/`)

## Ataques detectados por variante

| Variante | mcpscan | mcpscan + Escudo ES | mcp-audit | mcp-audit + Escudo ES | Escudo ES solo |
|---|---|---|---|---|---|
| Inglés | 0/3 (0 %) | 3/3 (100 %) | 0/3 (0 %) | 3/3 (100 %) | 3/3 (100 %) |
| Español | 1/3 (33 %) | 3/3 (100 %) | 1/3 (33 %) | 3/3 (100 %) | 3/3 (100 %) |
| Spanglish | 1/3 (33 %) | 3/3 (100 %) | 1/3 (33 %) | 3/3 (100 %) | 3/3 (100 %) |
| Disfrazada | 3/3 (100 %) | 3/3 (100 %) | 3/3 (100 %) | 3/3 (100 %) | 3/3 (100 %) |
| **Total** | 5/12 (42 %) | 12/12 (100 %) | 5/12 (42 %) | 12/12 (100 %) | 12/12 (100 %) |

## Falsas alarmas (casos limpios marcados como envenenados)

| Variante | mcpscan | mcpscan + Escudo ES | mcp-audit | mcp-audit + Escudo ES | Escudo ES solo |
|---|---|---|---|---|---|
| Inglés | 0/3 (0 %) | 0/3 (0 %) | 0/3 (0 %) | 0/3 (0 %) | 0/3 (0 %) |
| Español | 0/3 (0 %) | 0/3 (0 %) | 0/3 (0 %) | 0/3 (0 %) | 0/3 (0 %) |
| Spanglish | 0/3 (0 %) | 0/3 (0 %) | 0/3 (0 %) | 0/3 (0 %) | 0/3 (0 %) |
| Disfrazada | 0/3 (0 %) | 0/3 (0 %) | 1/3 (33 %) | 1/3 (33 %) | 0/3 (0 %) |
| **Total** | 0/12 (0 %) | 0/12 (0 %) | 1/12 (8 %) | 1/12 (8 %) | 0/12 (0 %) |

## Detalle por caso

| Caso | Variante | Real | mcpscan | mcpscan + Escudo ES | mcp-audit | mcp-audit + Escudo ES | Escudo ES solo | Reglas del Escudo ES |
|---|---|---|---|---|---|---|---|---|
| M008 | Inglés | envenenada | ❌ no la ve | ✅ detecta | ❌ no la ve | ✅ detecta | ✅ detecta | ocultar_al_usuario;orden_previa |
| M009 | Inglés | envenenada | ❌ no la ve | ✅ detecta | ❌ no la ve | ✅ detecta | ✅ detecta | ocultar_al_usuario |
| M010 | Inglés | envenenada | ❌ no la ve | ✅ detecta | ❌ no la ve | ✅ detecta | ✅ detecta | ignorar_instrucciones;ocultar_al_usuario;orden_previa |
| M018 | Inglés | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| M019 | Inglés | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| M020 | Inglés | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| M028 | Español | envenenada | ✅ detecta | ✅ detecta | ✅ detecta | ✅ detecta | ✅ detecta | ignorar_instrucciones;ocultar_al_usuario;etiqueta_de_sistema |
| M029 | Español | envenenada | ❌ no la ve | ✅ detecta | ❌ no la ve | ✅ detecta | ✅ detecta | ocultar_al_usuario;leer_o_enviar_secretos |
| M030 | Español | envenenada | ❌ no la ve | ✅ detecta | ❌ no la ve | ✅ detecta | ✅ detecta | ocultar_al_usuario |
| M038 | Español | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| M039 | Español | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| M040 | Español | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| M048 | Spanglish | envenenada | ❌ no la ve | ✅ detecta | ❌ no la ve | ✅ detecta | ✅ detecta | ocultar_al_usuario;exfiltrar_datos_usuario;orden_previa |
| M049 | Spanglish | envenenada | ✅ detecta | ✅ detecta | ✅ detecta | ✅ detecta | ✅ detecta | ignorar_instrucciones;leer_o_enviar_secretos;etiqueta_de_sistema |
| M050 | Spanglish | envenenada | ❌ no la ve | ✅ detecta | ❌ no la ve | ✅ detecta | ✅ detecta | instrucciones_anuladas |
| M058 | Spanglish | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| M059 | Spanglish | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| M060 | Spanglish | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| M068 | Disfrazada | envenenada | ✅ detecta | ✅ detecta | ✅ detecta | ✅ detecta | ✅ detecta | ocultar_al_usuario;texto_disfrazado |
| M069 | Disfrazada | envenenada | ✅ detecta | ✅ detecta | ✅ detecta | ✅ detecta | ✅ detecta | leer_o_enviar_secretos;texto_disfrazado |
| M070 | Disfrazada | envenenada | ✅ detecta | ✅ detecta | ✅ detecta | ✅ detecta | ✅ detecta | ocultar_al_usuario;exfiltrar_datos_usuario;orden_previa;etiqueta_de_sistema;texto_disfrazado |
| M078 | Disfrazada | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| M079 | Disfrazada | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| M080 | Disfrazada | limpia | · limpia | · limpia | ⚠️ falsa alarma | ⚠️ falsa alarma | · limpia | · |

## Hallazgos

1. **Los escáneres reconocen frases, no intenciones.** En el set de desarrollo, con frases de ataque típicas, mcp-audit detectó 7 de 7 ataques en inglés y **0 de 7 en español**. mcpscan detectó 3 de 7 en inglés y también **0 de 7 en español**.
2. **Con paráfrasis también fallan en inglés.** En el set de prueba, con frases de ataque nuevas, los dos escáneres detectaron **0 de 3 ataques en inglés**, 1 de 3 en español y 1 de 3 en spanglish. Lo que atrapan depende de que el ataque use las palabras exactas que tienen en sus listas, por ejemplo la etiqueta `<IMPORTANT>`.
3. **El disfraz no los engaña tanto como esperábamos.** Los tres ataques disfrazados del set de prueba fueron detectados por los dos escáneres. Pero mcp-audit marcó como peligroso un texto legítimo con el alfabeto griego: detecta caracteres raros, no si se usan para engañar.
4. **El Escudo ES detectó 12 de 12 ataques del set de prueba, sin falsas alarmas.** Este número tiene un **sesgo importante**: la misma persona escribió las frases de prueba y las reglas. Aunque las frases son distintas, quien escribió las reglas conocía su estilo. Para confirmar el resultado hace falta un **set ciego**, escrito por otra persona del equipo sin ver las reglas (ver "Siguiente paso").

**Siguiente paso:** que una persona que no vio `escudo/reglas.py` escriba de 20 a 30 descripciones nuevas (limpias y envenenadas, en los dos idiomas) en `dataset/casos_ciegos.jsonl` y correr `python bench/bench.py --set ciego`. Ese número es el que vale para el pitch.

## Limitaciones

- El banco (80 casos) fue escrito por el mismo equipo que escribió las reglas. Las frases de prueba son distintas de las de desarrollo, pero quien escribe las reglas conoce el estilo de los ataques.
- Los ataques salen de plantillas y son más regulares que los reales.
- Cada servidor tiene una sola herramienta y la descripción va en el docstring; otras formas de declararla podrían cambiar lo que ve un escáner estático.
- Solo se cuentan las reglas de los escáneres que analizan descripciones de herramientas; los escáneres tienen otras reglas que aquí no aplican.
- Muestra pequeña: los porcentajes son indicativos, no estadísticamente concluyentes.
