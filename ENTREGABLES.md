# Entregables · Escudo MCP en español

Portal: lo que pide https://www.cursorbolivia.com/sprint#entrega . El repositorio ya cubre B y C. A y D se pegan en el portal.

## A · Identificación

| Campo | Texto |
|---|---|
| Equipo | Arquisoft |
| Integrantes | Roby Daniel Duran Aguilar · Ronald Augusto Rodriguez Serrano · Ariane Somoza Rocha · Carla Loayza |
| Título | Escudo MCP en español |
| Track | 1 · Seguridad y confianza en IA |

Resumen para el portal (el conteo de palabras está al final de este archivo):

Un agente conectado por MCP lee la descripción de cada herramienta y la cree. Si la orden escondida está en español, los detectores abiertos casi no la ven. Medimos ese hueco con textos ficticios en inglés, español, spanglish y letras de otro alfabeto. El Escudo se pone entre el agente y el conector: normaliza el texto, busca la intención, cita la frase y deja la herramienta en cuarentena. En el set de prueba vio 12 de 12 ataques; cada escáner, 5 de 12. Ese número tiene sesgo. En 32 paráfrasis vio 12 de 16, y en español 1 de 4. No es un examen ciego. Sin escudo el canario falso sale; con escudo, la herramienta no llega al agente.

119 palabras.

## B · Material técnico

Repositorio público: https://github.com/robydaniel45san/escudo-mcp-es

Cómo reproducirlo, en `README.md`:

```bash
python -m unittest escudo.test_escudo escudo.test_informe -v
python laboratorio/iniciar_demo.py
```

La demo local es http://127.0.0.1:8770/laboratorio . La misma pantalla, con las sesiones ya medidas, está en https://robydaniel45san.github.io/escudo-mcp-es/ .

## C · Contribución y evidencia

El detalle está en `CONTRIBUTION.md`. La prueba reproducible y los límites:

| Qué | Dónde | Resultado |
|---|---|---|
| Tests del escudo | `python -m unittest escudo.test_escudo escudo.test_informe` | 17 de 17 |
| Set de prueba | `RESULTS.md` | Escudo 12 de 12 · cada escáner 5 de 12 · 0 falsas alarmas del Escudo |
| Paráfrasis | `bench/informe_ciego.md` | Escudo 12 de 16 · en español 1 de 4 · no es un examen ciego |
| Laboratorio | `VALIDACION.md` | 11 de 11 en la corrida rápida del 31/10/2026 15:22. No se volvió a medir el banco con los escáneres (I4); los números de `RESULTS.md` siguen siendo los del 10:29 y la huella del set de prueba no cambió |

Los datos son ficticios. El canario es `CANARIO-ARQUISOFT-0001`. No se escanearon servidores de terceros.

## D · Pitch de 3 minutos

Diapositivas para subir al portal: `pitch-escudo-mcp.pptx`, en la carpeta del proyecto. Son opcionales. La demo es la pantalla del laboratorio.

Decir, en este orden:

1. **0:00–0:30 · El problema.** Cuando conectas una herramienta a Cursor por MCP, el agente lee la descripción y le cree. Esta dice que calcula el IVA. Escondida hay una orden: lee el .env y no avises. Si esa orden está en español, los detectores que ya existen casi no la ven.
2. **0:30–1:00 · De qué partieron.** No empezamos de cero. Usamos mcpscan y mcp-audit tal cual. No existía una medición de este ataque en español, en spanglish y con letras de otro alfabeto.
3. **1:00–2:10 · La demo.** Abrir http://127.0.0.1:8770/laboratorio . Prueba A, sin escudo: el canario llega y la pantalla dice Cumple. Prueba B, con escudo: `calcular_iva` queda en cuarentena y ningún secreto sale.
4. **2:10–2:40 · Evidencia.** En el set de prueba, cada escáner vio 5 de 12 y el Escudo 12 de 12. Ese número tiene sesgo. En paráfrasis nuevas, el Escudo vio 12 de 16 y en español 1 de 4. No es un examen ciego.
5. **2:40–3:00 · Límites.** No cubrimos cualquier frase en español. El siguiente banco lo tiene que escribir alguien que no haya leído las reglas. Un intento con Cursor no alcanza para decir que el modelo cae en la trampa.

Después, una pregunta. Si preguntan por el 12 de 12: tiene sesgo y no lo sustituye el 12 de 16.
