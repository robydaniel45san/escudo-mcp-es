# Set ciego: instrucciones para quien escribe los casos

Gracias por ayudar. Tu trabajo hace que nuestro resultado sea creíble ante el jurado.

## Por qué existe este set
El Escudo ES detectó 12 de 12 ataques en nuestra prueba, pero la misma persona escribió los ataques y las reglas que los detectan. Es como si un profesor se corrigiera su propio examen. Tú vas a escribir casos **sin ver las reglas**, y ese será el número que presentemos.

## Antes de empezar: lo que NO debes abrir
No mires estos archivos hasta terminar y congelar tus casos:
- `escudo/` (las reglas del detector)
- `dataset/casos*.jsonl` y `dataset/generar.py` (los ataques que ya escribimos)
- `RESULTS.md`, `bench/` y `docs/02-pitch.md`
- El laboratorio T1-07 de la web Misión Sprint

Tampoco le preguntes al resto del equipo cómo funciona el escudo. Si ya viste alguno de estos archivos, avisa: buscamos a otra persona.

## Qué escribir
Descripciones de **herramientas MCP inventadas**. Una descripción es el texto que explica qué hace una herramienta, por ejemplo "Calcula el tiempo de entrega de un pedido según la ciudad". El agente de IA lee ese texto y le cree.

Escribe **entre 24 y 32 casos** en [`casos_ciegos.csv`](casos_ciegos.csv), repartidos así:

| Variante | Limpias | Envenenadas | Qué significa |
|----------|---------|-------------|---------------|
| `en` | 3 o 4 | 3 o 4 | Todo en inglés |
| `es` | 3 o 4 | 3 o 4 | Todo en español |
| `spanglish` | 3 o 4 | 3 o 4 | Mezcla de español e inglés, como se habla en un equipo de desarrollo |
| `disfrazada` | 3 o 4 | 3 o 4 | Escríbela normal: el conversor la disfraza solo (ver abajo) |

### Envenenadas: qué tipo de ataque esconder
Cada descripción envenenada empieza como una herramienta normal y después esconde una orden para el agente. Usa una o dos de estas intenciones, **con tus propias palabras**. No copies frases de internet ni de guías de seguridad:

| Técnica (columna `tecnica`) | Intención que tiene que tener la orden |
|-----------------------------|----------------------------------------|
| `ignorar` | Que el agente deje de seguir las instrucciones que ya tenía |
| `ocultar` | Que el agente le esconda algo a la persona usuaria |
| `secretos` | Que el agente lea o envíe claves, contraseñas, credenciales o archivos privados |
| `previa` | Que el agente haga algo extra antes de usar la herramienta o a escondidas |

Sé creativa o creativo: varía los verbos, el orden y el tono. Una orden puede sonar amable, técnica o como una "nota del desarrollador". Mientras más natural, mejor prueba.

### Limpias: herramientas legítimas, algunas difíciles
La mitad de las limpias pueden ser simples. La otra mitad deberían ser **difíciles**: herramientas legítimas que mencionan contraseñas, usuarios, archivos, claves o "antes de usar". Por ejemplo, una herramienta real que cambia contraseñas. Sirven para medir las falsas alarmas.

### Variante disfrazada
Escribe la descripción normal, en el idioma que quieras. Al convertir, las envenenadas se disfrazan solas: se cambian algunas letras por letras cirílicas idénticas y se insertan caracteres invisibles. En las limpias puedes usar palabras legítimas en otros alfabetos (griego, ruso) o emojis.

## Formato del CSV
Ábrelo con cualquier editor de texto o con Excel y guárdalo como **CSV UTF-8**.

| Columna | Valores |
|---------|---------|
| `id` | `C01`, `C02`, … sin repetir |
| `variante` | `en`, `es`, `spanglish` o `disfrazada` |
| `envenenada` | `si` o `no` |
| `tecnica` | En envenenadas: `ignorar`, `ocultar`, `secretos`, `previa` o dos unidas con `+` (por ejemplo `ocultar+secretos`). En limpias: `ninguna` |
| `descripcion` | El texto. Si tiene comas, va entre comillas dobles |

Reglas de contenido:
- Todo **inventado**: nada de claves, correos o nombres de empresas reales.
- Cada descripción entre 1 y 3 oraciones.

## Cuando termines
Desde la carpeta `escudo-mcp-es`:

```bash
# 1. Validar y convertir (también calcula la huella SHA-256)
python dataset/ciego/convertir.py
```

Después avisa al equipo. **El resto del equipo** hace lo siguiente, en este orden:
1. Commit del set ciego, **antes de medir nada**, con la huella en el mensaje.
2. `python bench/bench.py --set ciego --out bench/informe_ciego.md`
3. **No se tocan las reglas después de ver el resultado.** Si alguien las ajusta, se presentan los dos números: antes y después del ajuste.
