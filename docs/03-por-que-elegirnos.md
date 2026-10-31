# 03 · Por qué elegirnos

Argumentos para dos públicos: el **jurado** del sprint y los posibles **auspiciantes** o mentores que quieran acompañar el proyecto después del evento.

---

## Para el jurado: cómo respondemos a la rúbrica

| Criterio | Pts | Nuestro argumento | Dónde se comprueba |
|----------|-----|-------------------|--------------------|
| Contribución propia | 30 | Una medición que no encontramos publicada: cómo responden los escáneres MCP a ataques en español. Más una capa nueva que la mejora | `CONTRIBUTION.md`, `RESULTS.md` |
| Calidad técnica y funcionamiento | 25 | Flujo corto y demostrable: escanear, comparar y resaltar. Corre en local sin cuentas ni claves | Demo en vivo, README |
| Evidencia y pruebas | 20 | Banco etiquetado, set de prueba separado antes de ajustar, métricas por variante y falsas alarmas a la vista | `bench/`, `RESULTS.md` |
| Relevancia e impacto | 15 | MCP es como Cursor, el anfitrión, se conecta a herramientas. Los ataques llegan en el idioma de la víctima | Pitch, bloque 1 |
| Claridad de presentación | 10 | Una idea, una demo y una tabla | `02-pitch.md` |

**En una frase:** *no prometemos un producto, demostramos un hueco de seguridad con números y mostramos cómo cerrarlo.*

### Lo que nos diferencia de otras propuestas
- **No reinventamos:** usamos los escáneres existentes como línea base y les sumamos lo que les falta.
- **Hacemos una pregunta medible:** el resultado sirve aunque no nos favorezca.
- **Es local y regional:** el español es el idioma de nuestros usuarios y de quienes los atacan.
- **Es honesto:** el set de prueba se separa antes de ajustar, y las falsas alarmas se cuentan y se explican.

---

## Para auspiciantes y mentores: qué apoyan

Este es el **primer modelo (v0)**: una prueba de concepto para el sprint. Si el resultado confirma el hueco, el proyecto puede crecer así:

| Etapa | Qué se entrega | Qué necesitaríamos |
|-------|----------------|--------------------|
| v0 · Sprint (31/10) | Banco inicial, Escudo ES con reglas, medición y demo | El sprint mismo |
| v1 · Banco abierto | Banco público de ataques MCP en español con licencia abierta, para que otros equipos aporten casos | Mentoría en seguridad de IA y revisión del banco |
| v2 · Integración | Las reglas del Escudo ES como aporte a escáneres abiertos existentes | Tiempo de desarrollo y contacto con mantenedores |
| v3 · Comunidad | Talleres en universidades de Bolivia sobre seguridad de agentes de IA, usando Misión Sprint como material | Espacios y créditos de herramientas de IA |

**Por qué apoyarlo:**
- **Beneficia a toda la comunidad:** el banco y las reglas serían abiertos, no un producto cerrado.
- **Cubre un idioma desatendido:** la mayoría de las pruebas de seguridad de IA están en inglés.
- **Llega a estudiantes:** el material de aprendizaje ya existe y está pensado para quien nunca vio ciberseguridad.
- **Es medible:** cada etapa tiene un entregable que se puede revisar.

> Las etapas v1 a v3 son una propuesta del equipo. No hay compromisos con terceros ni auspicios confirmados.

---

## Qué tenemos ya preparado

- Documentación completa del proyecto: plan por fases, pitch, trazabilidad y reglas.
- Material de aprendizaje: **Misión Sprint**, con el caso T1-07 jugable y su laboratorio (privado hasta que se comparta).
- Un banco de demostración de 13 casos que muestra el tipo de evidencia que vamos a producir. **No es el resultado del sprint:** el resultado real se mide el día del evento.
