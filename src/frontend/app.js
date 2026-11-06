/* =============================================================================
 * Frontend de la Tienda Online
 *
 * Este frontend NO accede a TiendaService ni a los modelos del servidor:
 * todo se hace con peticiones HTTP (fetch) a la API REST de FastAPI.
 *
 * Endpoints utilizados:
 *   GET    /productos                  -> cargarProductos()
 *   POST   /productos                  -> crearProducto()
 *   DELETE /productos/{id}             -> eliminarProducto()
 *   GET    /usuarios                   -> cargarUsuarios()
 *   POST   /usuarios                   -> crearUsuario()
 *   POST   /pedidos                    -> crearPedido()
 *   GET    /usuarios/{id}/pedidos      -> verPedidos()
 * ========================================================================== */

// -----------------------------------------------------------------------------
// Dirección de la API (modificable desde la cabecera de la página)
// -----------------------------------------------------------------------------
const API_POR_DEFECTO = location.protocol.startsWith("http")
  ? location.origin                 // servido por FastAPI en /tienda
  : "http://localhost:8000";        // index.html abierto con doble clic

function leerApiGuardada() {
  try { return localStorage.getItem("api_url"); } catch { return null; }
}
let API_URL = leerApiGuardada() || API_POR_DEFECTO;

// Estado en memoria (lo que devolvió la API la última vez)
let productos = [];
let usuarios = [];

// -----------------------------------------------------------------------------
// Función central que realiza TODAS las peticiones a la API
// -----------------------------------------------------------------------------
async function api(metodo, ruta, cuerpo) {
  const opciones = { method: metodo, headers: {} };
  if (cuerpo !== undefined) {
    opciones.headers["Content-Type"] = "application/json";
    opciones.body = JSON.stringify(cuerpo);          // datos enviados como JSON
  }

  const respuesta = await fetch(API_URL + ruta, opciones);
  const datos = await respuesta.json().catch(() => null);  // respuesta JSON

  if (!respuesta.ok) {                                 // código HTTP 4xx / 5xx
    throw new Error(`HTTP ${respuesta.status}: ${mensajeDeError(datos)}`);
  }
  return datos;
}

function mensajeDeError(datos) {
  if (!datos || !datos.detail) return "error desconocido";
  if (typeof datos.detail === "string") return datos.detail;
  // Errores de validación de Pydantic (422): lista de errores
  return datos.detail.map(e => e.msg.replace(/^Value error, /, "")).join(" · ");
}

// -----------------------------------------------------------------------------
// Utilidades de interfaz
// -----------------------------------------------------------------------------
const $ = sel => document.querySelector(sel);
const euros = n => n.toLocaleString("es-ES", { style: "currency", currency: "EUR" });
const escapar = t => String(t ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function aviso(texto, esError = false) {
  const div = document.createElement("div");
  div.className = "aviso" + (esError ? " error" : "");
  div.textContent = texto;
  $("#avisos").appendChild(div);
  setTimeout(() => div.remove(), esError ? 6000 : 3500);
}

const NOMBRES_TIPO = { generico: "Genérico", electronico: "Electrónica", ropa: "Ropa" };

// =============================================================================
// PRODUCTOS
// =============================================================================
async function cargarProductos() {
  try {
    productos = await api("GET", "/productos");                 // GET /productos
    pintarProductos();
    pintarSelectoresProductos();
  } catch (e) { aviso(e.message, true); }
}

function pintarProductos() {
  const filtro = $("#filtro-tipo").value;
  const lista = productos.filter(p => !filtro || p.tipo === filtro);
  const cont = $("#lista-productos");

  if (lista.length === 0) {
    cont.innerHTML = `<div class="vacio">No hay productos.</div>`;
    return;
  }
  cont.innerHTML = lista.map(p => {
    let detalle = "";
    if (p.tipo === "electronico") detalle = `Garantía: ${p.meses_garantia} meses`;
    if (p.tipo === "ropa") detalle = `Talla ${escapar(p.talla)} · ${escapar(p.color)}`;
    return `
      <article class="tarjeta ${p.tipo}">
        <div class="visual">${ICONOS[p.tipo] || ICONOS.generico}</div>
        <div class="cuerpo">
          <span class="tipo">${NOMBRES_TIPO[p.tipo] || p.tipo} · #${p.id.slice(0, 8)}</span>
          <h3>${escapar(p.nombre)}</h3>
          <span class="detalle">${detalle || "&nbsp;"}</span>
          <span class="precio">${euros(p.precio)}</span>
          <div class="pie">
            <span class="stock ${p.stock < 5 ? "bajo" : ""}">Stock: ${p.stock}</span>
            <button class="peligro" data-eliminar="${p.id}">Eliminar</button>
          </div>
        </div>
      </article>`;
  }).join("");
}

// Iconos decorativos de cada tipo de producto
const ICONOS = {
  electronico: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M2 20h20"/></svg>`,
  ropa: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20.4 3.5 16 2a4 4 0 0 1-8 0L3.6 3.5a2 2 0 0 0-1.3 2.2l.6 3.5a1 1 0 0 0 1 .8H6v10a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V10h2.1a1 1 0 0 0 1-.8l.6-3.5a2 2 0 0 0-1.3-2.2z"/></svg>`,
  generico: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="M3 8l9 5 9-5"/><path d="M12 13v8"/></svg>`,
};


async function crearProducto(evento) {
  evento.preventDefault();
  const f = new FormData(evento.target);
  const tipo = f.get("tipo");
  const datos = {
    tipo,
    nombre: f.get("nombre"),
    precio: parseFloat(f.get("precio")),
    stock: parseInt(f.get("stock"), 10),
  };
  if (tipo === "electronico") datos.meses_garantia = f.get("meses_garantia") === "" ? null : parseInt(f.get("meses_garantia"), 10);
  if (tipo === "ropa") { datos.talla = f.get("talla"); datos.color = f.get("color"); }

  try {
    const nuevo = await api("POST", "/productos", datos);       // POST /productos
    aviso(`Producto "${nuevo.nombre}" creado (id ${nuevo.id.slice(0, 8)})`);
    evento.target.reset();
    actualizarCamposProducto();
    cargarProductos();
  } catch (e) { aviso(e.message, true); }
}

async function eliminarProducto(id) {
  const prod = productos.find(p => p.id === id);
  if (!confirm(`¿Eliminar "${prod ? prod.nombre : id}"?`)) return;
  try {
    const r = await api("DELETE", `/productos/${id}`);           // DELETE /productos/{id}
    aviso(r.message);
    cargarProductos();
  } catch (e) { aviso(e.message, true); }
}

function actualizarCamposProducto() {
  const tipo = $("#producto-tipo").value;
  document.querySelectorAll(".solo-electronico").forEach(el => el.classList.toggle("oculto", tipo !== "electronico"));
  document.querySelectorAll(".solo-ropa").forEach(el => el.classList.toggle("oculto", tipo !== "ropa"));
}

// =============================================================================
// USUARIOS
// =============================================================================
async function cargarUsuarios() {
  try {
    usuarios = await api("GET", "/usuarios");                    // GET /usuarios
    pintarUsuarios();
    pintarSelectoresUsuarios();
  } catch (e) { aviso(e.message, true); }
}

function pintarUsuarios() {
  $("#tabla-usuarios").innerHTML = usuarios.map(u => `
    <tr>
      <td title="${u.id}">${u.id.slice(0, 8)}</td>
      <td><span class="persona"><span class="avatar">${escapar(u.nombre.charAt(0).toUpperCase())}</span>${escapar(u.nombre)}</span></td>
      <td>${escapar(u.email)}</td>
      <td><span class="etiqueta ${u.es_admin ? "admin" : ""}">${u.es_admin ? "Administrador" : "Cliente"}</span></td>
    </tr>`).join("") || `<tr><td colspan="4">No hay usuarios.</td></tr>`;
}

async function crearUsuario(evento) {
  evento.preventDefault();
  const f = new FormData(evento.target);
  const datos = {
    nombre: f.get("nombre"),
    email: f.get("email"),
    tipo: f.get("tipo"),
    direccion_postal: f.get("direccion_postal") || null,
  };
  try {
    const nuevo = await api("POST", "/usuarios", datos);         // POST /usuarios
    aviso(`Usuario "${nuevo.nombre}" creado (id ${nuevo.id.slice(0, 8)})`);
    evento.target.reset();
    cargarUsuarios();
  } catch (e) { aviso(e.message, true); }
}

function pintarSelectoresUsuarios() {
  const clientes = usuarios.filter(u => !u.es_admin);
  const opciones = clientes.map(u => `<option value="${u.id}">${escapar(u.nombre)}</option>`).join("");
  const selPedido = $("#pedido-cliente");
  const previo = selPedido.value;
  selPedido.innerHTML = opciones;
  if (previo) selPedido.value = previo;

  const selVer = $("#pedidos-usuario");
  const previoVer = selVer.value;
  selVer.innerHTML = usuarios.map(u => `<option value="${u.id}">${escapar(u.nombre)}${u.es_admin ? " (admin)" : ""}</option>`).join("");
  if (previoVer) selVer.value = previoVer;
}

// =============================================================================
// NUEVO PEDIDO
// =============================================================================
function opcionesProductos() {
  return productos.map(p =>
    `<option value="${p.id}" ${p.stock === 0 ? "disabled" : ""}>${escapar(p.nombre)} — ${euros(p.precio)} (stock ${p.stock})</option>`
  ).join("");
}

function anadirLinea() {
  const div = document.createElement("div");
  div.className = "linea";
  div.innerHTML = `
    <select class="linea-producto">${opcionesProductos()}</select>
    <input class="linea-cantidad" type="number" min="1" step="1" value="1">
    <span class="subtotal">0,00 €</span>
    <button type="button" class="peligro" title="Quitar">✕</button>`;
  div.querySelector("button").onclick = () => { div.remove(); calcularTotal(); };
  div.addEventListener("input", calcularTotal);
  $("#lineas-pedido").appendChild(div);
  calcularTotal();
}

function pintarSelectoresProductos() {
  document.querySelectorAll(".linea-producto").forEach(sel => {
    const previo = sel.value;
    sel.innerHTML = opcionesProductos();
    if (previo) sel.value = previo;
  });
  calcularTotal();
}

function leerLineas() {
  return [...document.querySelectorAll(".linea")].map(div => ({
    div,
    producto_id: div.querySelector(".linea-producto").value,
    cantidad: parseInt(div.querySelector(".linea-cantidad").value, 10) || 0,
  }));
}

function calcularTotal() {
  let total = 0;
  for (const l of leerLineas()) {
    const p = productos.find(x => x.id === l.producto_id);
    const sub = p ? p.precio * l.cantidad : 0;
    l.div.querySelector(".subtotal").textContent = euros(sub);
    total += sub;
  }
  $("#total-pedido").textContent = euros(total);
}

async function crearPedido(evento) {
  evento.preventDefault();
  const items = leerLineas()
    .filter(l => l.producto_id)
    .map(({ producto_id, cantidad }) => ({ producto_id, cantidad }));
  if (items.length === 0) { aviso("Añade al menos un producto al pedido", true); return; }

  const datos = { cliente_id: $("#pedido-cliente").value, items };
  try {
    const pedido = await api("POST", "/pedidos", datos);         // POST /pedidos
    aviso(`Pedido ${pedido.id.slice(0, 8)} creado. Total: ${euros(pedido.total)}`);
    $("#lineas-pedido").innerHTML = "";
    anadirLinea();
    cargarProductos();                                           // el stock ha cambiado
    $("#pedidos-usuario").value = pedido.cliente_id;
  } catch (e) { aviso(e.message, true); }
}

// =============================================================================
// PEDIDOS DE UN USUARIO
// =============================================================================
async function verPedidos() {
  const id = $("#pedidos-usuario").value;
  if (!id) return;
  try {
    const pedidos = await api("GET", `/usuarios/${id}/pedidos`); // GET /usuarios/{id}/pedidos
    const cont = $("#lista-pedidos");
    if (pedidos.length === 0) {
      cont.innerHTML = `<div class="vacio">Este usuario no tiene pedidos.</div>`;
      return;
    }
    cont.innerHTML = pedidos.map(p => `
      <article class="pedido">
        <div class="pedido-cabecera">
          <strong>Pedido #${p.id.slice(0, 8)} · ${escapar(p.cliente_nombre)}</strong>
          <span>${new Date(p.fecha).toLocaleString("es-ES")}</span>
        </div>
        <table>
          ${p.items.map(i => `
            <tr><td>${i.cantidad} × ${escapar(i.nombre)} <small>(${euros(i.precio_unitario)})</small></td><td>${euros(i.subtotal)}</td></tr>`).join("")}
          <tr class="total"><td>Total</td><td>${euros(p.total)}</td></tr>
        </table>
      </article>`).join("");
  } catch (e) { aviso(e.message, true); }
}

// =============================================================================
// Conexión con el servidor y arranque
// =============================================================================
async function comprobarServidor() {
  const estado = $("#estado-api");
  try {
    await api("GET", "/usuarios");
    estado.textContent = "Conectado";
    estado.className = "estado ok";
    return true;
  } catch {
    estado.textContent = "Sin conexión";
    estado.className = "estado ko";
    return false;
  }
}

async function cargarTodo() {
  if (await comprobarServidor()) {
    await Promise.all([cargarProductos(), cargarUsuarios()]);
    if (!document.querySelector(".linea")) anadirLinea();
  } else {
    aviso(`No se puede conectar con la API en ${API_URL}`, true);
  }
}

function cambiarSeccion(id) {
  document.querySelectorAll(".pestana").forEach(b => b.classList.toggle("activa", b.dataset.seccion === id));
  document.querySelectorAll(".seccion").forEach(s => s.classList.toggle("activa", s.id === id));
  if (id === "pedidos") verPedidos();
}

document.addEventListener("DOMContentLoaded", () => {
  $("#api-url").value = API_URL;
  $("#form-servidor").addEventListener("submit", e => {
    e.preventDefault();
    API_URL = $("#api-url").value.trim().replace(/\/+$/, "");
    try { localStorage.setItem("api_url", API_URL); } catch { /* sin almacenamiento */ }
    cargarTodo();
  });

  document.querySelectorAll(".pestana").forEach(b => b.addEventListener("click", () => cambiarSeccion(b.dataset.seccion)));

  $("#filtro-tipo").addEventListener("change", pintarProductos);
  $("#recargar-productos").addEventListener("click", cargarProductos);
  $("#recargar-usuarios").addEventListener("click", cargarUsuarios);
  $("#producto-tipo").addEventListener("change", actualizarCamposProducto);
  $("#form-producto").addEventListener("submit", crearProducto);
  $("#form-usuario").addEventListener("submit", crearUsuario);
  $("#form-pedido").addEventListener("submit", crearPedido);
  $("#anadir-linea").addEventListener("click", anadirLinea);
  $("#ver-pedidos").addEventListener("click", verPedidos);
  $("#lista-productos").addEventListener("click", e => {
    const id = e.target.dataset.eliminar;
    if (id) eliminarProducto(id);
  });

  cargarTodo();
});
