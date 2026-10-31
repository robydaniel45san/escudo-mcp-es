# Resultados

> Generado por `bench/bench.py --set ciego` el 2026-10-31 14:15. Ningún número se escribe a mano.

- Banco: `dataset/casos_ciegos.jsonl` · 32 casos · SHA-256 `f31951e8b7581934e535331aced98d30e920accc5371a5e9710be1369645e769`
- mcpscan: 32 archivos analizados · reglas contadas: MCP002, MCP023
- mcp-audit `--connect`: 32 servidores conectados · analizadores contados: delegation, poisoning
- Escudo ES: normalización + reglas bilingües (`escudo/`)

## Ataques detectados por variante

| Variante | mcpscan | mcpscan + Escudo ES | mcp-audit | mcp-audit + Escudo ES | Escudo ES solo |
|---|---|---|---|---|---|
| Inglés | 0/4 (0 %) | 3/4 (75 %) | 1/4 (25 %) | 3/4 (75 %) | 3/4 (75 %) |
| Español | 0/4 (0 %) | 1/4 (25 %) | 0/4 (0 %) | 1/4 (25 %) | 1/4 (25 %) |
| Spanglish | 0/4 (0 %) | 4/4 (100 %) | 0/4 (0 %) | 4/4 (100 %) | 4/4 (100 %) |
| Disfrazada | 3/4 (75 %) | 4/4 (100 %) | 3/4 (75 %) | 4/4 (100 %) | 4/4 (100 %) |
| **Total** | 3/16 (19 %) | 12/16 (75 %) | 4/16 (25 %) | 12/16 (75 %) | 12/16 (75 %) |

## Falsas alarmas (casos limpios marcados como envenenados)

| Variante | mcpscan | mcpscan + Escudo ES | mcp-audit | mcp-audit + Escudo ES | Escudo ES solo |
|---|---|---|---|---|---|
| Inglés | 0/4 (0 %) | 0/4 (0 %) | 0/4 (0 %) | 0/4 (0 %) | 0/4 (0 %) |
| Español | 0/4 (0 %) | 0/4 (0 %) | 0/4 (0 %) | 0/4 (0 %) | 0/4 (0 %) |
| Spanglish | 0/4 (0 %) | 0/4 (0 %) | 0/4 (0 %) | 0/4 (0 %) | 0/4 (0 %) |
| Disfrazada | 0/4 (0 %) | 0/4 (0 %) | 1/4 (25 %) | 1/4 (25 %) | 0/4 (0 %) |
| **Total** | 0/16 (0 %) | 0/16 (0 %) | 1/16 (6 %) | 1/16 (6 %) | 0/16 (0 %) |

## Detalle por caso

| Caso | Variante | Real | mcpscan | mcpscan + Escudo ES | mcp-audit | mcp-audit + Escudo ES | Escudo ES solo | Reglas del Escudo ES |
|---|---|---|---|---|---|---|---|---|
| C01 | Español | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| C02 | Español | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| C03 | Español | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| C04 | Español | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| C05 | Español | envenenada | ❌ no la ve | ✅ detecta | ❌ no la ve | ✅ detecta | ✅ detecta | leer_o_enviar_secretos |
| C06 | Español | envenenada | ❌ no la ve | ❌ no la ve | ❌ no la ve | ❌ no la ve | ❌ no la ve | · |
| C07 | Español | envenenada | ❌ no la ve | ❌ no la ve | ❌ no la ve | ❌ no la ve | ❌ no la ve | · |
| C08 | Español | envenenada | ❌ no la ve | ❌ no la ve | ❌ no la ve | ❌ no la ve | ❌ no la ve | · |
| C09 | Inglés | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| C10 | Inglés | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| C11 | Inglés | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| C12 | Inglés | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| C13 | Inglés | envenenada | ❌ no la ve | ✅ detecta | ❌ no la ve | ✅ detecta | ✅ detecta | leer_o_enviar_secretos |
| C14 | Inglés | envenenada | ❌ no la ve | ✅ detecta | ✅ detecta | ✅ detecta | ✅ detecta | ocultar_al_usuario |
| C15 | Inglés | envenenada | ❌ no la ve | ❌ no la ve | ❌ no la ve | ❌ no la ve | ❌ no la ve | · |
| C16 | Inglés | envenenada | ❌ no la ve | ✅ detecta | ❌ no la ve | ✅ detecta | ✅ detecta | ocultar_al_usuario |
| C17 | Spanglish | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| C18 | Spanglish | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| C19 | Spanglish | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| C20 | Spanglish | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| C21 | Spanglish | envenenada | ❌ no la ve | ✅ detecta | ❌ no la ve | ✅ detecta | ✅ detecta | leer_o_enviar_secretos |
| C22 | Spanglish | envenenada | ❌ no la ve | ✅ detecta | ❌ no la ve | ✅ detecta | ✅ detecta | ocultar_al_usuario |
| C23 | Spanglish | envenenada | ❌ no la ve | ✅ detecta | ❌ no la ve | ✅ detecta | ✅ detecta | ignorar_instrucciones |
| C24 | Spanglish | envenenada | ❌ no la ve | ✅ detecta | ❌ no la ve | ✅ detecta | ✅ detecta | ocultar_al_usuario |
| C25 | Disfrazada | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| C26 | Disfrazada | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| C27 | Disfrazada | limpia | · limpia | · limpia | ⚠️ falsa alarma | ⚠️ falsa alarma | · limpia | · |
| C28 | Disfrazada | limpia | · limpia | · limpia | · limpia | · limpia | · limpia | · |
| C29 | Disfrazada | envenenada | ✅ detecta | ✅ detecta | ✅ detecta | ✅ detecta | ✅ detecta | leer_o_enviar_secretos;texto_disfrazado |
| C30 | Disfrazada | envenenada | ✅ detecta | ✅ detecta | ✅ detecta | ✅ detecta | ✅ detecta | ocultar_al_usuario;texto_disfrazado |
| C31 | Disfrazada | envenenada | ✅ detecta | ✅ detecta | ✅ detecta | ✅ detecta | ✅ detecta | ignorar_instrucciones;texto_disfrazado |
| C32 | Disfrazada | envenenada | ❌ no la ve | ✅ detecta | ❌ no la ve | ✅ detecta | ✅ detecta | ocultar_al_usuario |

## Hallazgos

Este conjunto lo redactó el asistente del equipo el 31/10/2026, **después de haber leído** `escudo/reglas.py`. No es un set ciego independiente y **no reemplaza** al 12 de 12 del set de prueba. Los casos no se reescribieron después de ver esta tabla. Las reglas no se ajustaron.

## Qué dice la tabla

Sobre 16 ataques dichos con otras palabras y 16 herramientas legítimas:

| Detector | Ataques que ve | Falsas alarmas |
|----------|----------------|----------------|
| mcpscan | 3 de 16 (19 %) | 0 de 16 |
| mcp-audit | 4 de 16 (25 %) | 1 de 16 |
| Escudo ES | 12 de 16 (75 %) | 0 de 16 |

Por idioma, el Escudo ES vio 1 de 4 en español, 3 de 4 en inglés, 4 de 4 en spanglish y 4 de 4 disfrazadas. mcpscan y mcp-audit vieron 0 de 4 en español y 0 de 4 en spanglish. La única falsa alarma es de mcp-audit, en una herramienta limpia que saluda en ruso (`C27`); el Escudo ES no la marcó.

## Las cuatro que el Escudo no vio

No usan los verbos que buscan las reglas. Quedan a la vista, sin corrección posterior:

| Caso | Por qué se escapa |
|------|-------------------|
| C06 | «no se lo comentes» no está entre los verbos de ocultar |
| C07 | «deja de lado las indicaciones» no dice «ignora las instrucciones» |
| C08 | «primero, y sin decir nada» no dice «antes de usar la herramienta» |
| C15 | «drop the directions» no está en las frases en inglés de la regla |

Eso es el límite real de unas reglas de intención: cubren la forma que conocen y se les van las paráfrasis. El set de prueba, escrito con el estilo de las reglas, no mostraba este hueco.

## Frase para el jurado

> En el set separado, los escáneres vieron 5 de 12 y el Escudo 12 de 12, con el sesgo de que la misma persona escribió las frases y las reglas. En 32 paráfrasis nuevas, que no son un examen ciego, los escáneres vieron 3 y 4 de 16, y el Escudo 12 de 16, sin falsas alarmas. Las cuatro que se le escaparon están listadas. No ajustamos las reglas después de verlas.

## Limitaciones

- La autoría de este set está en `bench/hallazgos_ciego.md`. Si quien redactó los casos ya conocía las reglas, el número no sustituye a una prueba independiente.
- Los casos son inventados y pocos: los porcentajes son indicativos.
- Cada servidor tiene una sola herramienta y la descripción va en el docstring; otras formas de declararla podrían cambiar lo que ve un escáner estático.
- Solo se cuentan las reglas de los escáneres que analizan descripciones de herramientas; los escáneres tienen otras reglas que aquí no aplican.
