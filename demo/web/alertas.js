/* Ventanas de alerta del Escudo MCP, compartidas por todas las páginas.
 *
 *   alertaEscudo({nivel, titulo, texto, hora, detalle})
 *     nivel: "critica" | "alta" | "media" | "ok"
 *     Las críticas abren una ventana modal que hay que cerrar; las demás aparecen
 *     como avisos en la esquina y se van solas después de unos segundos.
 */
(function () {
  const css = `
  .ae-pila{position:fixed;top:80px;right:16px;z-index:1000;display:grid;gap:8px;width:min(380px,calc(100vw - 32px))}
  .ae{border-radius:12px;padding:12px 16px;display:grid;gap:4px;border:2px solid;background:var(--surface,#fff);color:var(--ink,#17171A);
      box-shadow:0 12px 32px rgba(0,0,0,.25);animation:ae-in .5s cubic-bezier(0.22,1,0.36,1) both;font-family:var(--font,system-ui)}
  .ae .ae-h{display:flex;justify-content:space-between;gap:8px;align-items:start}
  .ae b{font-size:16px;line-height:24px} .ae p{margin:0;font-size:14px;line-height:20px}
  .ae .ae-t{font-family:var(--mono,ui-monospace,monospace);font-size:12px;line-height:16px;opacity:.8}
  .ae button{all:unset;cursor:pointer;font-size:14px;line-height:20px;padding:0 4px;border-radius:4px}
  .ae button:focus-visible{outline:2px solid currentColor}
  .ae.critica{border-color:var(--crit,#C0352B)} .ae.critica b{color:var(--crit,#C0352B)}
  .ae.alta,.ae.media{border-color:var(--warn,#9A5B00)} .ae.alta b,.ae.media b{color:var(--warn,#9A5B00)}
  .ae.ok{border-color:var(--ok,#16803C)} .ae.ok b{color:var(--ok,#16803C)}
  .ae-modal{border:0;padding:0;border-radius:16px;max-width:min(560px,calc(100vw - 32px));background:var(--surface,#fff);color:var(--ink,#17171A)}
  .ae-modal::backdrop{background:rgba(0,0,0,.55)}
  .ae-modal .in{padding:24px;display:grid;gap:12px;border:3px solid var(--crit,#C0352B);border-radius:16px;font-family:var(--font,system-ui)}
  .ae-modal .k{font-family:var(--mono,ui-monospace,monospace);font-size:12px;line-height:16px;letter-spacing:.08em;text-transform:uppercase;color:var(--crit,#C0352B)}
  .ae-modal h2{margin:0;font-size:24px;line-height:32px;color:var(--crit,#C0352B)}
  .ae-modal p{margin:0;font-size:16px;line-height:24px}
  .ae-modal pre{margin:0;font-family:var(--mono,ui-monospace,monospace);font-size:12px;line-height:16px;background:var(--sunken,#F0F0EC);border-radius:8px;padding:12px;white-space:pre-wrap;overflow-wrap:anywhere;max-height:200px;overflow:auto}
  .ae-modal .b{justify-self:end;font:inherit;font-size:16px;font-weight:600;padding:8px 12px;border-radius:8px;border:1px solid var(--crit,#C0352B);background:var(--crit,#C0352B);color:#fff;cursor:pointer}
  @keyframes ae-in{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}
  @media (prefers-reduced-motion:reduce){.ae{animation:none}}`;
  const st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
  const pila = document.createElement("div"); pila.className = "ae-pila"; pila.setAttribute("role", "status"); pila.setAttribute("aria-live", "assertive");
  document.addEventListener("DOMContentLoaded", () => document.body.appendChild(pila));
  if (document.body) document.body.appendChild(pila);
  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const icono = { critica: "⛔", alta: "⚠", media: "⚠", ok: "✓" };

  window.alertaEscudo = function ({ nivel = "media", titulo, texto = "", hora = "", detalle = "" }) {
    if (nivel === "critica" && typeof HTMLDialogElement === "function") {
      const d = document.createElement("dialog"); d.className = "ae-modal";
      d.innerHTML = `<div class="in"><span class="k">${icono.critica} Alerta crítica del Escudo MCP ${hora ? "· " + esc(hora) : ""}</span>
        <h2>${esc(titulo)}</h2><p>${esc(texto)}</p>${detalle ? `<pre>${esc(detalle)}</pre>` : ""}
        <button class="b" autofocus>Entendido</button></div>`;
      d.querySelector(".b").onclick = () => d.close();
      d.addEventListener("close", () => d.remove());
      document.body.appendChild(d); d.showModal(); return;
    }
    const a = document.createElement("div"); a.className = "ae " + nivel;
    a.innerHTML = `<div class="ae-h"><b>${icono[nivel] || "⚠"} ${esc(titulo)}</b><button aria-label="Cerrar alerta">✕</button></div>
      ${hora ? `<span class="ae-t">${esc(hora)}</span>` : ""}<p>${esc(texto)}</p>`;
    a.querySelector("button").onclick = () => a.remove();
    pila.prepend(a);
    setTimeout(() => a.remove(), nivel === "ok" ? 4000 : 9000);
    while (pila.children.length > 5) pila.lastChild.remove();
  };

  /* Convierte un evento estandarizado del laboratorio en una alerta (o en nada). */
  window.alertaDesdeEvento = function (e) {
    const hora = (e["@timestamp"] || "").slice(11, 23);
    if (e.severity_id >= 5) return alertaEscudo({ nivel: "critica", titulo: "Un secreto salió del agente", texto: e.mensaje, hora,
      detalle: `${e["span.name"]}\nseverity: ${e.severity_id} ${e.severity} · disposition: ${e.disposition}` });
    if (e.evento === "escudo.rug_pull") return alertaEscudo({ nivel: "alta", titulo: "Rug pull detectado", texto: e.mensaje, hora });
    if (e.evento === "escudo.salida_bloqueada") return alertaEscudo({ nivel: "alta", titulo: "Respuesta envenenada retenida", texto: e.mensaje, hora });
    if (e.evento === "escudo.exfiltracion_bloqueada") return alertaEscudo({ nivel: "alta", titulo: "Robo de secreto bloqueado", texto: e.mensaje, hora });
    if (e.evento === "escudo.cuarentena") return alertaEscudo({ nivel: "alta", titulo: `Herramienta en cuarentena: ${e["gen_ai.tool.name"] || ""}`, texto: e.mensaje, hora });
    if (e.evento === "escudo.llamada_bloqueada") return alertaEscudo({ nivel: "media", titulo: "Llamada bloqueada", texto: e.mensaje, hora });
    if (e.severity_id === 3 && e.componente === "conector") return alertaEscudo({ nivel: "media", titulo: "El agente usó una herramienta envenenada", texto: e.mensaje, hora });
  };
})();
