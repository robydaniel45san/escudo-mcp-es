# 04 · Trazabilidad

Cada fila parte de una frase del texto oficial del sprint y la sigue hasta el componente que la cumple, la prueba que lo demuestra, el criterio de la rúbrica y el entregable.

**Códigos:** rúbrica R1 contribución (30) · R2 técnica (25) · R3 evidencia (20) · R4 impacto (15) · R5 presentación (10). Entregables E-A identificación · E-B repositorio · E-C contribución y evidencia · E-D pitch. Reglas REG-1 entornos propios · REG-2 datos ficticios · REG-3 declarar lo previo · REG-4 licencias · REG-5 no falsificar.

## Preguntas oficiales del Track 1 que responde

| Código | Pregunta oficial |
|--------|------------------|
| T1-Q2 | ¿Cómo evaluar su resistencia a instrucciones no confiables dentro de un entorno de pruebas? |
| T1-Q4 | ¿Cómo comparar distintos sistemas de revisión para detectar errores? |
| T1-Q5 | ¿Cómo crear pruebas relevantes para aplicaciones de IA en español? |

## Matriz

| Requisito | Texto oficial de origen | Componente | Prueba / evidencia | Rúbrica | Entregable | Fase |
|-----------|-------------------------|------------|--------------------|---------|------------|------|
| T1-07-REQ-01 Banco etiquetado de descripciones limpias y envenenadas | T1-Q2 "instrucciones no confiables… entorno de pruebas" | `dataset/casos.jsonl` | Número de casos por variante y etiqueta | R3 | E-C | 2 |
| T1-07-REQ-02 Variantes en español, spanglish y disfrazadas | T1-Q5 "pruebas… en español" | `dataset/` + `DATASET.md` | Distribución por variante | R1, R4 | E-C | 2 |
| T1-07-REQ-03 Set de prueba separado antes de ajustar | Criterio "pruebas más reproducibles" | `dataset/casos_prueba.jsonl` | Fecha y hora de congelado en `DATASET.md` | R3, REG-5 | E-C | 2 |
| T1-07-REQ-04 Línea base con escáneres existentes | T1-Q4 "comparar distintos sistemas de revisión" | `bench/bench.py --baseline` | Detección por variante sin escudo | R3 | E-C | 3 |
| T1-07-REQ-05 Normalización de homoglifos y caracteres invisibles | Track 1 "resistentes a… manipulaciones" | `escudo/normalizar.py` | Tests con casos disfrazados | R1, R2 | E-B | 2 |
| T1-07-REQ-06 Reglas bilingües de intención con frase culpable | Track 1 "trazabilidad" | `escudo/reglas.py` | Cada regla con un ejemplo que activa y otro que no | R1, R2 | E-B | 2 |
| T1-07-REQ-07 Comparación antes y después | Criterio "una mejora defendible" | `bench/` → `RESULTS.md` | Tabla base frente a escudo, por variante | R1, R3 | E-C | 3 |
| T1-07-REQ-08 Falsas alarmas contadas y explicadas | Criterio "errores y limitaciones claramente reportados" | `RESULTS.md` | Lista de falsas alarmas con su causa | R3, REG-5 | E-C | 3 |
| T1-07-REQ-09 Demo con servidor MCP de juguete | Entregable D "solo mockups no demuestran el funcionamiento" | `demo/` | Demo en vivo y video de respaldo | R2, R5 | E-D | 2, 5 |
| T1-07-REQ-10 Un comando reproduce todo | Entregable B "README de cómo ejecutarlo" | `README.md` | Alguien ajeno lo ejecuta desde cero | R2 | E-B | 4 |
| T1-07-REQ-11 Declarar lo previo y lo hecho | Bases "aclarar qué existía antes" | `CONTRIBUTION.md` | Lista antes y durante, con horas | R1, REG-3 | E-C | 1, 4 |
| T1-07-REQ-12 Licencias de terceros | Bases "reconocer autoría y licencia" | `THIRD_PARTY.md` | Cada herramienta con su licencia | REG-4 | E-C | 4 |
| T1-07-REQ-13 Sin datos reales ni claves | Bases "usá datos ficticios" | Todo el repo | Revisión antes de entregar | REG-1, REG-2 | Todos | 4 |
| T1-07-REQ-14 Resumen de 120 palabras como máximo | Entregable A | Portal de entrega | Conteo de palabras | R5 | E-A | 4 |

## Estado

| Requisito | Estado |
|-----------|--------|
| REQ-01 a REQ-14 | Pendiente: se ejecuta durante el sprint |
| Documentación de soporte | Lista (esta carpeta) |
