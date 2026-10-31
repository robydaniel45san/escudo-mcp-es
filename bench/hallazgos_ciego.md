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
