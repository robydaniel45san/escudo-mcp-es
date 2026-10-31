# 00 · Por qué esta propuesta y qué cumplimos

Fuentes oficiales revisadas el 31/10/2026:
- Página del sprint: https://www.cursorbolivia.com/sprint#entrega
- Bases: https://www.cursorbolivia.com/sprint/reglas
- Preguntas frecuentes de la página (respuestas desplegadas)

**Leyenda de estado:**
- ✅ **Cumplido:** ya está resuelto en el diseño o en la documentación.
- ⏳ **Durante el sprint:** se cumple al ejecutar el plan; la fase indica cuándo.
- ⚠️ **A confirmar:** depende de la organización o de una prueba previa.

---

## Parte 1 · Por qué elegimos el T1-07

### 1.1 Comparación con las otras 12 propuestas

Evaluamos las 13 propuestas con las preguntas que más pesan en la rúbrica: ¿ya está resuelto?, ¿es medible?, ¿se demuestra en 3 minutos?, ¿le importa al jurado?

| Propuesta | ¿Ya existe una solución madura? | Aporte nuevo verificable (30 pts) | Demo en 3 min | Relevancia para Cursor | Factible en 6 h |
|-----------|-------------------------------|-----------------------------------|---------------|------------------------|-----------------|
| **T1-07 Escudo MCP en español** | **No encontramos medición en español** | **Alto: medición nueva + capa propia** | **Alta** | **Directa: Cursor usa MCP** | Sí |
| T1-01 Agente con permisos | Sí: LlamaFirewall, NeMo Guardrails, Lakera | Medio | Alta | Media | Sí |
| T1-02 Evaluador de respuestas | Sí: Ragas, evaluadores de fidelidad | Medio | Media | Baja | Sí |
| T1-03 Banco en español | Parcial: MAPS es multilingüe general | Medio | Baja | Media | Sí |
| T1-04 Monitor de agentes | Sí: herramientas de trazas | Bajo | Alta | Media | Sí |
| T1-05 Comparador de revisores | Parcial | Medio | Media | Baja | Justo |
| T1-06 Protección de RAG | Sí: varias defensas publicadas | Medio | Alta | Media | Sí |
| T2-01 Analista de registros | Sí: SIEM comerciales | Bajo | Alta | Baja | Sí |
| T2-02 Asistente Sigma | Parcial | Medio | Media | Baja | Sí |
| T2-03 Clasificador de phishing | Sí, hay muchos; en español hay datos de correo (SpaPhish) | Bajo | Alta | Baja | Sí |
| T2-04 Generador de reportes | Parcial | Medio | Media | Baja | Sí |
| T2-05 Priorización contextual | Sí: EPSS y KEV ya se usan así | Bajo | Media | Baja | Sí |
| T2-06 Correlador de alertas | Sí: SIEM comerciales | Bajo | Media | Baja | Sí |

### 1.2 Las cinco razones

1. **Responde una pregunta que nadie respondió todavía.** Hay escáneres abiertos para tool poisoning, y las guías del ataque mencionan el cambio de idioma como forma de evadir filtros. Pero no encontramos ninguna medición publicada para el español. Eso vale en el criterio más pesado: **contribución propia, 30 pts**.
2. **Gana aunque el resultado no nos favorezca.** Las preguntas frecuentes oficiales lo dicen: *"Un resultado negativo bien documentado puede ser valioso. Importan la pregunta, el método y la honestidad."*
3. **Se apoya en lo que ya existe, como piden las bases.** Usamos escáneres abiertos como línea base y les sumamos lo que les falta. Las bases permiten reutilizar proyectos *"si la licencia lo permite, lo atribuís y hacés un aporte nuevo verificable"*.
4. **Le importa al jurado.** MCP es como Cursor, el anfitrión, conecta herramientas externas.
5. **Cabe en 6 horas con 4 personas.** Hay cuatro carriles independientes (banco, escudo, demo y medición) y un orden de recorte definido.

---

## Parte 2 · Qué cumplimos, sección por sección

### 2.1 Método ("Cómo funciona")
| Lo que pide la página | Cómo lo cumplimos | Estado |
|-----------------------|-------------------|--------|
| 01 · Elegir uno de los dos tracks | Track 1 · AI Security & AI Safety | ✅ |
| 02 · Identificar una pregunta concreta | *¿Los escáneres de MCP detectan igual un ataque en español que en inglés, y cuánto mejora una capa bilingüe?* | ✅ |
| 03 · Equipo de cuatro y decidir qué construir o comprobar | Cuatro roles definidos en el README; falta anotar los nombres | ⏳ Fase 1 |
| 04 · Mostrar qué había antes, qué hicieron y qué demuestra el resultado | `CONTRIBUTION.md` + `RESULTS.md` + pitch | ⏳ Fases 3 y 4 |

### 2.2 Track 1
| Lo que pide la página | Cómo lo cumplimos | Estado |
|-----------------------|-------------------|--------|
| Proteger y evaluar aplicaciones y agentes de IA ante manipulaciones | Evaluamos detectores de manipulación en las herramientas que usan los agentes | ✅ |
| Pregunta: resistencia a instrucciones no confiables en un entorno de pruebas | Banco de descripciones envenenadas en un entorno local | ✅ diseño · ⏳ Fase 2 |
| Pregunta: comparar distintos sistemas de revisión | Escáneres base frente a escáner + Escudo ES | ✅ diseño · ⏳ Fase 3 |
| Pregunta: pruebas relevantes para IA en español | Variantes en español, spanglish y disfrazadas | ✅ diseño · ⏳ Fase 2 |
| Mejora defendible: "pruebas más reproducibles o un método de evaluación con errores y limitaciones claramente reportados" | Set de prueba separado, un comando reproduce todo, falsas alarmas reportadas | ⏳ Fases 3 y 4 |
| FAQ: en el Track 1 se puede proteger sistemas de IA sin integrar una IA nueva | El Escudo ES funciona con reglas; el juez LLM es opcional | ✅ |

### 2.3 Forma de contribuir
| Lo que pide la página | Cómo lo cumplimos | Estado |
|-----------------------|-------------------|--------|
| Una de cuatro formas: Construir, Extender, Adaptar o Investigar | **Investigar** (medición) + **Extender** (capa sobre escáneres existentes) | ✅ |
| "Cambiar solo el diseño, el nombre o los colores no alcanza" | El aporte es una medición y una lógica de detección nuevas | ✅ |

### 2.4 Entregables
| Entregable oficial | Qué entregamos | Dónde | Estado |
|--------------------|----------------|-------|--------|
| A · Identificación: equipo, título, track y resumen de 120 palabras como máximo | Título "Escudo MCP en español", Track 1 y el resumen | Portal de entrega | ⏳ Fase 4 |
| B · Repositorio o ZIP con README para reproducir | Esta carpeta como repositorio; README con un comando | `README.md` | ✅ estructura · ⏳ Fase 4 |
| C · Qué había antes, qué aportaron, al menos una prueba reproducible, origen de los datos y limitaciones | Plantillas listas | `CONTRIBUTION.md`, `DATASET.md`, `RESULTS.md` | ✅ plantillas · ⏳ Fase 4 |
| D · Pitch de hasta 3 minutos y una pregunta; solo mockups no alcanzan | Guion con los 5 bloques oficiales, demo real con servidor de juguete y video de respaldo | `docs/02-pitch.md` | ✅ guion · ⏳ Fase 5 |

### 2.5 Pitch (estructura oficial)
| Tiempo oficial | Bloque oficial | Nuestro guion | Estado |
|----------------|----------------|---------------|--------|
| 0:00–0:30 | El problema | La herramienta del IVA con la orden escondida | ✅ |
| 0:30–1:00 | De qué partieron | Escáneres existentes + banco nuevo | ✅ |
| 1:00–2:10 | La demo | Base "limpia" frente a escudo "envenenada" | ✅ guion · ⏳ demo |
| 2:10–2:40 | Pruebas o evidencia | Tabla por variante con números medidos | ⏳ Fase 3 |
| 2:40–3:00 | Limitaciones y siguiente paso | Banco propio, datos ficticios, sobreajuste; banco abierto | ✅ |

### 2.6 Reglas (bases)
| Regla oficial | Cómo la cumplimos | Estado |
|---------------|-------------------|--------|
| Cuatro integrantes, un solo proyecto | Un proyecto, cuatro roles | ⏳ nombres |
| Un track, declarado al entregar | Track 1 | ⏳ al entregar |
| Se puede usar Cursor y otros asistentes; el equipo entiende y prueba | Cada componente tiene un responsable y tests | ⏳ Fase 2 |
| Reutilizar código de terceros con autoría y licencia | `THIRD_PARTY.md` | ✅ plantilla · ⏳ Fase 4 |
| Aclarar qué existía antes y qué se hizo en las 6 horas | `CONTRIBUTION.md`: esta documentación se declara como material previo | ✅ |
| FAQ: se puede llegar con la idea preparada, declarando el material previo | Solo traemos documentación, sin código | ✅ |
| Solo entornos propios, simulados o autorizados | Servidor MCP de juguete en local | ✅ diseño |
| Fuera ataques a terceros, extracción de datos y credenciales ajenas | No escaneamos servidores de terceros; los secretos son ficticios | ✅ |
| No publicar claves, tokens, contraseñas ni datos personales | `.gitignore` excluye `.env`; revisión antes de entregar | ⏳ Fases 1 y 4 |
| No falsificar resultados | `RESULTS.md` lo genera el script; set de prueba separado | ✅ diseño |
| FAQ: no es obligatorio desplegar; basta una demo local reproducible | Demo local con Streamlit | ✅ |
| Código de conducta | El equipo lo acepta y lo respeta | ✅ |

### 2.7 Rúbrica (100 pts)
| Criterio | Pts | Cómo apuntamos a puntaje alto | Evidencia |
|----------|-----|-------------------------------|-----------|
| Contribución propia | 30 | Medición nueva para el español + Escudo ES | `CONTRIBUTION.md` |
| Calidad técnica y funcionamiento | 25 | Flujo principal demostrable y reproducible | Demo y README |
| Evidencia y pruebas | 20 | Banco etiquetado, set separado, falsas alarmas a la vista | `RESULTS.md` |
| Relevancia e impacto | 15 | Agentes como Cursor conectados por MCP; ataques en el idioma de la víctima | Pitch |
| Claridad de presentación | 10 | Una idea, una demo, una tabla | `02-pitch.md` |

### 2.8 Lo que queda a confirmar
| Tema | Por qué | Acción |
|------|---------|--------|
| ~~Escáneres que corren sin cuenta~~ | ✅ Resuelto el 31/10: mcpscan-cli y mcp-audit corren en local. Snyk Agent Scan queda excluido porque usa un servidor externo | Ver `THIRD_PARTY.md` |
| Fecha y hora límite de entrega | La página dice que se confirma con el programa | Revisar el portal de equipos y Luma |
| Autoría y propiedad intelectual | La FAQ remite a las bases aceptadas al inscribirse | Leerlas en el portal |
| Premios y formato de ganadores | La página dice "por confirmar" | No afecta el plan |

---

## Resumen

- **Cumplido en el diseño:** track, pregunta, forma de aporte, reglas de seguridad, uso de terceros, estructura de entregables y guion.
- **Se cumple durante el sprint:** banco, escudo, medición, demo, textos finales y nombres del equipo.
- **A confirmar:** escáneres locales, hora de entrega y bases firmadas.
