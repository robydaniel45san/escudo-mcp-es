# Contribución (entregable C)

## Qué existía antes del sprint
| Elemento | Origen | Uso en el proyecto |
|----------|--------|--------------------|
| Documentación de esta carpeta (`docs/`, README) | Preparada por el equipo antes del evento | Plan, pitch y trazabilidad |
| Escáneres MCP: _(nombre y versión)_ | Terceros, ver `THIRD_PARTY.md` | Línea base, sin modificar |
| SDK de MCP en Python | Terceros | Servidor de juguete de la demo |
| Entorno preparado: escáneres instalados y prueba de humo con **un solo caso en inglés** (31/10) | Equipo, antes del desarrollo | Confirmar que la línea base corre en local. No se midió ningún caso en español |

## Qué hicimos durante las 6 horas
Inicio: _(hora)_ · Fin: _(hora)_

| Componente | Descripción | Responsable |
|------------|-------------|-------------|
| `dataset/` | Banco de _(N)_ descripciones en 4 variantes | |
| `escudo/` | Normalización y reglas bilingües | |
| `bench/` | Medición y generación de `RESULTS.md` | |
| `demo/` | Servidor MCP de juguete e interfaz | |

## Prueba reproducible
```bash
python bench/bench.py --dataset dataset/casos_prueba.jsonl --out RESULTS.md
```

## Origen de los datos
Todos los casos son ficticios y fueron escritos por el equipo durante el sprint. Ver `DATASET.md`.
