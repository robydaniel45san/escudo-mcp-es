# Banco de pruebas

## Formato (`dataset/casos.jsonl`)
Una línea por caso:
```json
{"id": "M001", "variante": "es", "envenenada": true, "tecnica": "leer_secretos", "descripcion": "..."}
```
- `variante`: `en` · `es` · `spanglish` · `disfrazada`
- `tecnica`: `ignorar_instrucciones` · `ocultar_al_usuario` · `leer_secretos` · `orden_previa` · `ninguna`

## Distribución
| Variante | Limpias | Envenenadas | Total |
|----------|---------|-------------|-------|
| Inglés | | | |
| Español | | | |
| Spanglish | | | |
| Disfrazada | | | |

## Set de prueba
Separado el _(hora)_, antes de escribir las reglas del escudo. Archivo: `dataset/casos_prueba.jsonl` (_(N)_ casos, 30 %).

## Origen y licencia
Casos ficticios escritos por el equipo. Ningún secreto es real. Licencia: CC BY 4.0.
