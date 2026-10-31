# 05 · Reglas y riesgos

## Reglas del evento que aplican directamente

| Regla de las bases | Cómo la cumplimos |
|--------------------|-------------------|
| Solo entornos propios, simulados o autorizados | El servidor MCP es de juguete y corre en local. No escaneamos servidores de terceros. |
| Nada de ataques a terceros, extracción de datos ni credenciales ajenas | Los "secretos" del banco son ficticios (por ejemplo, `CLAVE-FICTICIA-0001`). |
| No publicar claves, tokens, contraseñas ni datos personales | Revisión del repositorio antes de entregar (paso 4.6 del plan). Un `.env` real nunca entra al repo. |
| Aclarar qué existía antes y qué se hizo en las 6 horas | `CONTRIBUTION.md` con horas de inicio y fin. |
| Reconocer autoría y licencia del código de terceros | `THIRD_PARTY.md`. |
| No falsificar resultados | Set de prueba separado y números tomados solo de `RESULTS.md`. |
| Se puede usar Cursor y otros asistentes | Lo usamos, y el equipo entiende y prueba cada parte. |

> **Confirmado en las preguntas frecuentes oficiales:** se puede llegar con la idea preparada. Se puede estudiar el problema y preparar el entorno, pero hay que declarar el material previo, porque se puntúa el avance durante el sprint. Esta carpeta contiene **solo documentación**, sin código, y se declara en `CONTRIBUTION.md`.

## Riesgos y cómo los mitigamos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Un escáner necesita cuenta, clave o internet | Media | Medio | Verificarlo en la fase 0 y usar solo los que corren en local |
| Sesgo: el banco lo escribe el mismo equipo | Alta | Medio | Quien escribe los casos (D) no escribe las reglas (N), y el set de prueba se separa antes |
| Reglas sobreajustadas al banco | Media | Alto | Medir solo sobre el set congelado y reportar las falsas alarmas |
| El escáner base sí detecta el español | Media | Bajo | Se presenta como hallazgo; el aporte pasa a ser el banco y las variantes disfrazadas |
| La demo falla en vivo | Baja | Alto | Video de respaldo grabado en la fase 5 |
| Falta tiempo | Media | Medio | Orden de recorte definido en el plan |
| Problemas con el wifi del evento | Media | Medio | Todo corre en local; las dependencias se instalan en la fase 0 |
