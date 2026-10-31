# 01 · Plan paso a paso

El trabajo tiene cinco fases. Cada paso dice **quién** lo hace, **qué** produce y **cuándo** está terminado.

| Fase | Cuándo | Objetivo |
|------|--------|----------|
| 0 · Preparación | Antes de que abra la ventana de desarrollo | Llegar sin dudas de reglas ni de herramientas |
| 1 · Arranque | 0:00–0:30 | Pregunta concreta, repositorio y roles |
| 2 · Construcción en paralelo | 0:30–2:30 | Banco, escudo, demo y medición listos por separado |
| 3 · Medición | 2:30–4:30 | Línea base, Escudo ES y comparación |
| 4 · Cierre y entrega | 4:30–5:15 | Resultados, documentación y entregables A, B y C |
| 5 · Pitch | 5:15–6:00 y presentación | Ensayo con reloj, video de respaldo y entregable D |

Roles: **N** = Núcleo técnico · **D** = Datos y pruebas · **I** = Interfaz y demo · **E** = Evidencia y pitch.

---

## Fase 0 · Preparación (antes de empezar)

Nada de código en esta fase: las bases piden declarar qué existía antes y qué se hizo en las 6 horas.

| # | Paso | Quién | Terminado cuando |
|---|------|-------|------------------|
| 0.1 | Leer las bases y las preguntas frecuentes oficiales. **Confirmado:** se puede llegar con la idea preparada si se declara el material previo | Todos | ✅ Hecho (ver `00-por-que-y-cumplimiento.md`) |
| 0.2 | Instalar Python (3.12 o superior), Git, Cursor y Streamlit en las 4 laptops | Todos | En la laptop principal ya están Python 3.14.5, Git 2.55 y Node 24 (31/10). Falta Streamlit y revisar las otras 3 laptops |
| 0.3 | Elegir 2 o 3 escáneres MCP abiertos y comprobar que corren **sin cuenta ni clave** | D | ✅ Hecho (31/10): **mcpscan-cli 0.21.0** y **mcp-audit 0.25.1** corren en local y pasaron la prueba de humo en inglés. Snyk Agent Scan queda excluido porque envía los datos a un servidor externo. Ver `THIRD_PARTY.md` |
| 0.4 | Leer el ataque: guía de PolicyLayer sobre instrucciones escondidas y el paper MCP-ITP | N, E | Cada uno puede explicar el tool poisoning en una frase |
| 0.5 | Revisar el SDK oficial de MCP en Python para el servidor de juguete | I | ✅ SDK `mcp` 1.30.0 instalado. Una herramienta se declara con `@mcp.tool()` y su descripción es el docstring |
| 0.6 | Repasar el caso T1-07 en Misión Sprint y el guion del pitch ([`02-pitch.md`](02-pitch.md)) | Todos | Todos cuentan el problema en 30 segundos |

---

## Fase 1 · Arranque (0:00–0:30)

| # | Paso | Quién | Terminado cuando |
|---|------|-------|------------------|
| 1.1 | Escribir la pregunta en una línea: *¿Los escáneres de MCP detectan igual un ataque en español que en inglés, y cuánto mejora una capa bilingüe?* | Todos | La pregunta está en el README |
| 1.2 | Crear el repositorio con esta estructura de carpetas y subir la documentación | E | Repositorio Git local creado con `.gitignore` para secretos (31/10). Falta el primer commit y subirlo a GitHub |
| 1.3 | Confirmar los roles y anotar los nombres en el README | Todos | La tabla de roles está completa |
| 1.4 | Acordar el formato del caso (JSONL): `id`, `variante`, `envenenada`, `descripcion`, `tecnica` | D, N | El formato está en `DATASET.md` |
| 1.5 | Registrar la hora de inicio en `CONTRIBUTION.md` | E | Queda la constancia de qué existía antes |

---

## Fase 2 · Construcción en paralelo (0:30–2:30)

Cuatro carriles independientes. Nadie espera a nadie hasta la fase 3.

### Carril D · Banco de pruebas (`dataset/`)
| # | Paso | Terminado cuando |
|---|------|------------------|
| 2.D1 | Escribir de 60 a 100 descripciones ficticias de herramientas MCP: la mitad limpias y la otra mitad envenenadas | El archivo `casos.jsonl` valida contra el formato |
| 2.D2 | Repartirlas en 4 variantes: inglés, español, spanglish y disfrazada (homoglifos y caracteres invisibles) | Cada variante tiene casos limpios y envenenados |
| 2.D3 | Incluir **limpias difíciles**: herramientas legítimas que hablan de contraseñas, archivos o usuarios | Hay al menos 10, para medir las falsas alarmas |
| 2.D4 | **Separar el set de prueba final (30 %) y no mirarlo** mientras N ajusta las reglas | `casos_prueba.jsonl` existe y queda congelado |

### Carril N · Escudo ES (`escudo/`)
| # | Paso | Terminado cuando |
|---|------|------------------|
| 2.N1 | Normalización: quitar caracteres de ancho cero, cambiar homoglifos cirílicos y griegos por letras latinas, minúsculas y sin tildes | Una función devuelve el texto limpio y tiene tests |
| 2.N2 | Reglas de intención en inglés y en español: ignorar instrucciones, ocultar al usuario, leer o enviar secretos, orden previa al uso | Cada regla tiene un ejemplo que la activa y otro que no |
| 2.N3 | Salida explicable: veredicto, regla activada y frase culpable | El resultado sirve para resaltar la frase en la demo |
| 2.N4 | (Opcional) Juez LLM que compara la descripción con el propósito declarado de la herramienta | Se puede activar o desactivar con un parámetro |

### Carril I · Demo (`demo/`)
| # | Paso | Terminado cuando |
|---|------|------------------|
| 2.I1 | Servidor MCP de juguete con 3 herramientas simuladas, una envenenada en spanglish | El servidor arranca en local |
| 2.I2 | Pantalla Streamlit: pegar una descripción y ver el veredicto de cada escáner con la frase resaltada | Funciona con texto fijo, aunque el escudo aún no esté conectado |
| 2.I3 | Vista "lo que ve una persona" frente a "lo que ve el escudo", con los caracteres invisibles marcados | Se entiende sin explicación |

### Carril E · Medición (`bench/`)
| # | Paso | Terminado cuando |
|---|------|------------------|
| 2.E1 | Script que corre cada escáner sobre el banco y guarda el veredicto por caso | Funciona con 5 casos de ejemplo |
| 2.E2 | Métricas por variante: recall, precisión y falsas alarmas | Sale una tabla en CSV |
| 2.E3 | Generar `RESULTS.md` automáticamente desde el CSV | Un solo comando produce la tabla |

**Punto de control a las 2:30:** banco completo, escudo con tests, demo con texto fijo y bench que corre. Si algo falta, se recorta el alcance, no se mueve la hora.

---

## Fase 3 · Medición (2:30–4:30)

| # | Paso | Quién | Terminado cuando |
|---|------|-------|------------------|
| 3.1 | Correr la **línea base**: escáneres existentes sobre todo el banco | D, E | Tabla de detección por variante, sin el escudo |
| 3.2 | Anotar los primeros hallazgos: qué variantes se escapan y por qué | E | Hay 3 frases de hallazgo en `RESULTS.md` |
| 3.3 | Ajustar las reglas del escudo **solo con el set de desarrollo** | N | Las reglas cubren los casos de desarrollo |
| 3.4 | Correr escáner + Escudo ES sobre el **set de prueba congelado** | D, E | Tabla antes y después con números finales |
| 3.5 | Conectar el escudo a la demo y probar el caso del pitch de punta a punta | I, N | La demo muestra base "limpia" y escudo "envenenada" |
| 3.6 | Revisar las falsas alarmas una por una y explicarlas | N, E | Cada falsa alarma tiene su causa escrita |

> **Si el escáner base detecta bien el español:** también es un resultado válido. Se presenta como hallazgo ("los escáneres ya cubren el español en X %") y el aporte pasa a ser el banco abierto en español y la cobertura de variantes disfrazadas.

---

## Fase 4 · Cierre y entrega (4:30–5:15)

| # | Paso | Quién | Entregable |
|---|------|-------|------------|
| 4.1 | Completar `RESULTS.md`: tabla, hallazgos, falsas alarmas y limitaciones | E | C |
| 4.2 | Completar `CONTRIBUTION.md`: qué existía antes y qué hicimos | E | C |
| 4.3 | Completar `THIRD_PARTY.md` con cada escáner y librería, y su licencia | D | C |
| 4.4 | Verificar el README: alguien que no es del equipo clona el repo y lo ejecuta desde cero | I | B |
| 4.5 | Escribir el resumen de 120 palabras como máximo | E | A |
| 4.6 | Revisar que no haya claves, tokens ni datos personales en el repo | N | Reglas |
| 4.7 | Subir todo al portal de entrega | E | A, B, C |

---

## Fase 5 · Pitch (5:15–6:00 y presentación)

| # | Paso | Quién | Terminado cuando |
|---|------|-------|------------------|
| 5.1 | Ensayar el guion de [`02-pitch.md`](02-pitch.md) con reloj, dos veces | E + todos | Sale en 3:00 o menos |
| 5.2 | Grabar un video corto de la demo como respaldo | I | El video está en la laptop y en la nube |
| 5.3 | Preparar la diapositiva única con la tabla antes y después | E | Se lee desde el fondo de la sala |
| 5.4 | Repartir las preguntas probables del jurado | Todos | Cada pregunta tiene quien la responda |

---

## Definición de terminado

El proyecto está terminado cuando:

- [ ] El banco tiene al menos 60 casos en 4 variantes, con un set de prueba separado.
- [ ] Existe una tabla de detección por variante: escáner base frente a escáner con Escudo ES.
- [ ] Las falsas alarmas están contadas y explicadas.
- [ ] La demo funciona en vivo y existe el video de respaldo.
- [ ] Un solo comando reproduce los resultados desde cero.
- [ ] Los entregables A, B, C y D están completos.
- [ ] Ninguna clave ni dato personal está en el repositorio.

## Qué se recorta si falta tiempo

En este orden:
1. El juez LLM opcional (2.N4).
2. La variante disfrazada con caracteres griegos (se dejan solo los cirílicos).
3. El tercer escáner de la línea base (alcanza con dos).
4. El banco baja de 100 a 60 casos.

**Nunca se recorta:** la línea base, el set de prueba separado ni el reporte de las limitaciones.
