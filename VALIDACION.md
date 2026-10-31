# Validación de la lógica principal

> Generado por `python validar.py` el 2026-10-31 13:49 sobre el commit `d5b871c`. Las invariantes están definidas en [`docs/08-logica-principal.md`](docs/08-logica-principal.md).

**Resultado: 12 de 12 invariantes se cumplen.**

| Invariante | Qué se comprueba | Resultado | Detalle |
|---|---|---|---|
| I1–I2 | Normalización y reglas bilingües (tests) | ✅ cumple | 17 tests · todos pasan |
| I3 | Set de prueba congelado sin cambios | ✅ cumple | SHA-256 dc2c207ecc4354a0… coincide |
| I4 | Medición reproducible (bench --set prueba) | ✅ cumple | 24 casos medidos de nuevo · decisiones idénticas |
| I5 | El hallazgo se sostiene (escáneres < escudo, y el español queda fuera) | ✅ cumple | prueba: mcpscan 5/12 · mcp-audit 5/12 · escudo 12/12 — desarrollo, mcp-audit: inglés 7/7 frente a español 0/7 |
| I6 | Sin escudo, el ataque es real: un agente obediente filtra el canario | ✅ cumple | sesión A-134840: 3 capturas del canario · vías seguidas por el agente: descripción, esquema, respuesta |
| I7 | Con escudo, ninguna herramienta envenenada llega al agente | ✅ cumple | sesión B-134844: en cuarentena ['calcular_iva', 'convertir_unidades'] · el agente vio ['buscar_factura', 'clima', 'tipo_de_cambio'] · capturas 0 |
| I8 | Un rug pull se bloquea | ✅ cumple | sesión C-134850: 1 rug pull detectado · capturas 0 |
| I9 | Una respuesta envenenada no llega al agente | ✅ cumple | sesión D-134855: 1 respuesta retenida · capturas 0 |
| I10 | Un argumento con forma de secreto no sale | ✅ cumple | sesión B-134844: 1 intento bloqueado · argumentos con canario que llegaron al conector: 0 |
| I11 | El escudo falla cerrado si el conector no responde | ✅ cumple | el agente recibe un error y ninguna herramienta sin revisar |
| I12 | Registro estandarizado: sesiones, punto clave y argumentos recortados | ✅ cumple | 97 eventos en 4 sesiones · un trace_id por sesión · punto clave en todas · argumentos recortados |
| I13 | El repositorio no contiene claves, .env reales ni logs | ✅ cumple | 63 archivos versionados · sin claves, .env ni logs |

Las pruebas de I6 a I12 usan el laboratorio local (conector malicioso :9100 y Escudo verificador :9200) con un agente obediente simulado y un canario falso. Ningún dato es real.
