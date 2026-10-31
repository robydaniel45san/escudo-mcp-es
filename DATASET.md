# Banco de pruebas

Generado con [`dataset/generar.py`](dataset/generar.py) (semilla 2026). Todos los casos son **ficticios**: ninguna herramienta, clave ni archivo es real.

## Formato
Una línea JSON por caso:
```json
{"id": "M001", "variante": "es", "envenenada": true, "tecnica": "ocultar+secretos", "grupo": "desarrollo", "descripcion": "..."}
```
- `variante`: `en` · `es` · `spanglish` · `disfrazada` (homoglifos cirílicos y caracteres invisibles sobre frases en, es o spanglish)
- `tecnica`: `ignorar` · `ocultar` · `secretos` · `previa`, o una combinación; `ninguna` en los casos limpios
- `grupo`: `desarrollo` (se usa para escribir y ajustar las reglas) o `prueba` (solo para la medición final)

## Distribución
| Variante | Limpias | Envenenadas | Total | Desarrollo | Prueba |
|----------|---------|-------------|-------|------------|--------|
| Inglés | 10 | 10 | 20 | 14 | 6 |
| Español | 10 | 10 | 20 | 14 | 6 |
| Spanglish | 10 | 10 | 20 | 14 | 6 |
| Disfrazada | 10 | 10 | 20 | 14 | 6 |
| **Total** | **40** | **40** | **80** | **56** | **24** |

Las limpias incluyen **casos difíciles**: herramientas legítimas que hablan de contraseñas, usuarios, archivos o variables de entorno, y textos con letras griegas, rusas o emojis reales. Sirven para medir las falsas alarmas.

## Set de prueba congelado
| Dato | Valor |
|------|-------|
| Archivo | `dataset/casos_prueba.jsonl` (24 casos) |
| Congelado | 2026-10-31 10:24, **antes de escribir las reglas del Escudo ES** |
| SHA-256 | `dc2c207ecc4354a004e77f392d30eecf4385870b6d8fd6b389f45a6711fd5ba7` |

Cualquiera puede comprobar que el set no cambió:
```bash
sha256sum dataset/casos_prueba.jsonl
```

**Frases separadas:** las frases de ataque del set de prueba son distintas de las de desarrollo. Cada técnica tiene paráfrasis propias para la prueba, así el escudo se mide sobre frases que no se usaron para escribir sus reglas.

## Límites conocidos
- El banco lo escribió el mismo equipo que escribe las reglas. Separar las frases reduce el sesgo, pero no lo elimina: quien escribe las reglas conoce el estilo de los ataques.
- Los ataques se arman con plantillas, así que son más regulares que los reales.
- Son 80 casos: los resultados son indicativos, no estadísticamente concluyentes.

## Licencia
CC BY 4.0.
