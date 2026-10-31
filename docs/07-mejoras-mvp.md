# 07 · Mejoras priorizadas para el MVP de demostración

Revisión hecha como ingeniería de ciberseguridad sobre el estado del 31/10/2026. Prioridades:
- **P0:** sin esto, la demo puede fallar o el escudo tiene un hueco conocido. Se hace antes de presentar.
- **P1:** suma puntos si sobra tiempo.
- **P2:** siguiente versión.

## 1. Modelo de amenazas (qué defiende el MVP)

| Amenaza (OWASP MCP Top 10, beta) | Cómo ataca | Defensa en el MVP | Estado |
|----------------------------------|------------|-------------------|--------|
| MCP03 · Tool poisoning en la **descripción** | Orden escondida en el texto de la herramienta | Escudo ES: normalización y reglas en inglés y español | ✅ |
| MCP03 · **Full-Schema Poisoning** (CyberArk) | Orden escondida en los **parámetros**: nombre, descripción, valor por defecto | Revisar el esquema completo, no solo la descripción | ✅ P0, hecho |
| MCP03 · **Envenenamiento de la respuesta** | La herramienta devuelve un "error" falso con una orden | Revisar cada respuesta antes de entregarla al agente | ✅ P0, hecho |
| MCP03 · Rug pull | La herramienta cambia después de aprobarla | Huella SHA-256 de la definición aprobada | ✅ (ahora cubre el esquema completo) |
| MCP01 · Exposición de secretos | El agente manda claves en los argumentos | Bloqueo de argumentos con forma de secreto | ✅ |
| Disfraz con homoglifos o invisibles | Letras cirílicas, caracteres de ancho cero | Normalización antes de las reglas | ✅ |
| Paráfrasis nuevas | Una orden dicha de otra forma | Reglas de intención; **falta** un juez con IA | ⚠️ P1 |

## 2. Prioridades

| # | Mejora | Por qué importa | Prioridad | Estado |
|---|--------|-----------------|-----------|--------|
| 1 | **Arranque en un comando** (`iniciar_demo.py`) con chequeos previos | En el escenario no hay tiempo de abrir tres terminales; un puerto ocupado arruina la demo | P0 | ✅ |
| 2 | **Revisar el esquema completo** de cada herramienta | Ataque real documentado (Full-Schema Poisoning) que el MVP no veía | P0 | ✅ |
| 3 | **Revisar las respuestas** de las herramientas | Una herramienta limpia puede envenenar al agente con su respuesta | P0 | ✅ |
| 4 | **Escenario D · envenenamiento avanzado** | Muestra en vivo los dos ataques nuevos y su bloqueo | P0 | ✅ |
| 5 | **Modo guion** de 3 minutos en el tablero | Guía los 5 bloques oficiales del pitch, con reloj | P0 | ✅ |
| 6 | **Set ciego** escrito por otra persona | Sin esto, el 12 de 12 tiene sesgo | P0 (equipo) | ⏳ |
| 7 | 3 intentos por carpeta con Cursor y otro modelo | Un solo intento no es evidencia | P1 (equipo) | ⏳ |
| 8 | Juez con IA como segunda opinión, activable | Cubre paráfrasis que las reglas no ven | P1 | ⏳ |
| 9 | **Fallar cerrado**: si el escudo no puede analizar, bloquea | Hoy un error interno devuelve error al agente; hay que garantizarlo con un test | P1 | ⏳ |
| 10 | Video de respaldo de la demo | Plan B si algo falla en vivo | P1 (equipo) | ⏳ |
| 11 | Manifiestos firmados de herramientas | Mitigación recomendada para rug pull a gran escala | P2 | — |
| 12 | Integrar las reglas como plugin de un escáner abierto | Llevar el aporte a la comunidad | P2 | — |

## 2b. Resultado de los escenarios con las mejoras (31/10/2026, 13:40)
| Escenario | Qué pasa |
|-----------|----------|
| A · sin escudo | El agente cae por las **tres vías**: descripción, parámetro y respuesta. El canario sale |
| B · con escudo | `calcular_iva` (descripción) y `convertir_unidades` (parámetro) en cuarentena. 0 robos |
| C · rug pull | La huella de la definición completa detecta el cambio. 0 robos |
| D · esquema y respuesta | La respuesta envenenada de `buscar_factura` llega retenida. 0 robos |

## 3. Checklist del día de la demo
1. `python laboratorio/iniciar_demo.py` → los tres servicios en verde.
2. Abrir `http://127.0.0.1:8770/laboratorio` y activar **Modo guion** y **Modo presentación**.
3. Correr los escenarios una vez antes de subir al escenario (el primer arranque es el más lento).
4. Tener abierto el video de respaldo.
5. Al terminar: Ctrl+C en la terminal del arranque detiene todo.

## Fuentes
- [CyberArk · Poison everywhere: No output from your MCP server is safe](https://www.cyberark.com/resources/home/poison-everywhere-no-output-from-your-mcp-server-is-safe)
- [OWASP MCP Top 10 (beta)](https://owasp.org/www-project-mcp-top-10/)
- [Nordic APIs · Guide to the OWASP MCP Top 10](https://nordicapis.com/guide-to-the-owasp-mcp-top-10/)
- [SecureW2 · MCP Tool Poisoning](https://securew2.com/blog/mcp-tool-poisoning-how-it-works-and-how-to-stop-it)
- [NULLCON Berlin 2025 · charla sobre MCP](https://berlin2025.nullcon.net/berlin-2025/speaker-speaker-your-mcp-server-executes-commands)
