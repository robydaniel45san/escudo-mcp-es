# Herramientas de terceros

Instaladas el 31/10/2026 en un entorno aislado (`.venv-scanners`, fuera del repositorio) con versiones fijas: ver [`requirements-scanners.txt`](requirements-scanners.txt).

| Herramienta | Versión | Licencia | Corre en local | Para qué la usamos | Enlace |
|-------------|---------|----------|----------------|--------------------|--------|
| mcpscan-cli | 0.21.0 | MIT | ✅ Sí, análisis estático sin red | Línea base: reglas MCP002 (tool poisoning) y MCP023 (anulación de políticas) sobre el código del servidor | https://github.com/glatinone/mcpscan |
| mcp-audit-scanner (con extra `[mcp]`) | 0.25.1 | Apache 2.0 | ✅ Sí: `scan` no usa red; `--connect` lee las descripciones en vivo de un servidor local | Línea base: analizadores `poisoning` y `delegation` sobre las descripciones reales de las herramientas | https://github.com/adudley78/mcp-audit |
| SDK de MCP para Python (`mcp`) | 1.30.0 | MIT | ✅ Sí | Servidor de juguete de la demo | https://github.com/modelcontextprotocol/python-sdk |
| snyk-agent-scan | 0.6.10 | Apache 2.0 | ❌ No: envía las descripciones a un servidor de verificación externo de Snyk | **Excluido de la línea base.** Usarlo implicaría enviar datos a un servicio externo y depender de su cuenta | https://github.com/snyk/agent-scan |
| Streamlit | pendiente | Apache 2.0 | ✅ Sí | Interfaz de la demo | https://streamlit.io |

No modificamos el código de terceros. Las reglas del Escudo ES son propias.

## Prueba de humo (31/10/2026, antes del desarrollo)

Solo para confirmar que los escáneres funcionan. Se usó **un único caso en inglés** sobre un servidor de juguete fuera del repositorio. El experimento en español se hace durante el sprint.

| Escáner | Resultado con el caso en inglés |
|---------|---------------------------------|
| mcpscan-cli | 3 hallazgos MCP002 (etiqueta `<IMPORTANT>`, "read ~/.ssh/id_rsa", "Do not tell the user") |
| mcp-audit `--connect` | 5 hallazgos de `poisoning` (exfiltración de clave SSH, inyección XML, anulación de comportamiento, manipulación entre herramientas, orden de secreto) y 1 de `delegation` |

Nota: mcp-audit guarda una línea base local de las herramientas escaneadas (detección de "rug pull"). Hay que tenerlo en cuenta al repetir los escaneos.
