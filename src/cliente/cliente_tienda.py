"""Cliente Python de la Tienda Online (Práctica 2 - Parte 2, Parte 1).

Script INDEPENDIENTE del servidor: no importa TiendaService, ni los modelos,
ni nada de la aplicación FastAPI. Toda la comunicación se hace con peticiones
HTTP usando la librería `requests`.

Uso:
    python cliente_tienda.py                          -> usa BASE_URL
    python cliente_tienda.py http://192.168.1.34:8000 -> usa la IP de otro equipo

Para la prueba entre dos equipos (Parte 2) basta con cambiar BASE_URL por la IP
del equipo que ejecuta la API, por ejemplo: BASE_URL = "http://192.168.1.34:8000"
"""

import sys
import time

import requests

# Dirección base de la API: cámbiala aquí para usar la API de otro equipo
BASE_URL = "http://localhost:8000"

TIMEOUT = 5  # segundos


# -----------------------------------------------------------------------------
# Utilidades
# -----------------------------------------------------------------------------
def comprobar_respuesta(respuesta: requests.Response, codigo_esperado: int, operacion: str):
    """Comprueba el código de estado HTTP y devuelve el JSON de la respuesta."""
    try:
        datos = respuesta.json()
    except ValueError:
        datos = None

    if respuesta.status_code == codigo_esperado:
        print(f"[OK]    {operacion} -> HTTP {respuesta.status_code}")
        return datos

    detalle = datos.get("detail") if isinstance(datos, dict) else respuesta.text
    print(f"[ERROR] {operacion} -> HTTP {respuesta.status_code}: {detalle}")
    return None


def titulo(texto: str):
    print("\n" + "=" * 60)
    print(texto)
    print("=" * 60)


# -----------------------------------------------------------------------------
# Operaciones contra la API
# -----------------------------------------------------------------------------
def crear_usuario(nombre: str, email: str, tipo: str = "cliente", direccion_postal: str | None = None):
    datos = {"nombre": nombre, "email": email, "tipo": tipo, "direccion_postal": direccion_postal}
    r = requests.post(f"{BASE_URL}/usuarios", json=datos, timeout=TIMEOUT)  # POST /usuarios
    return comprobar_respuesta(r, 201, f"Crear usuario '{nombre}'")


def listar_usuarios():
    r = requests.get(f"{BASE_URL}/usuarios", timeout=TIMEOUT)  # GET /usuarios
    return comprobar_respuesta(r, 200, "Listar usuarios") or []


def obtener_usuario(usuario_id: int):
    r = requests.get(f"{BASE_URL}/usuarios/{usuario_id}", timeout=TIMEOUT)  # GET /usuarios/{id}
    return comprobar_respuesta(r, 200, f"Obtener usuario {usuario_id}")


def crear_producto(**datos):
    r = requests.post(f"{BASE_URL}/productos", json=datos, timeout=TIMEOUT)  # POST /productos
    return comprobar_respuesta(r, 201, f"Crear producto '{datos.get('nombre')}'")


def listar_productos():
    r = requests.get(f"{BASE_URL}/productos", timeout=TIMEOUT)  # GET /productos
    return comprobar_respuesta(r, 200, "Listar productos") or []


def crear_pedido(cliente_id: int, items: list[dict]):
    datos = {"cliente_id": cliente_id, "items": items}
    r = requests.post(f"{BASE_URL}/pedidos", json=datos, timeout=TIMEOUT)  # POST /pedidos
    return comprobar_respuesta(r, 201, f"Crear pedido para el cliente {cliente_id[:8]}")


def pedidos_de_usuario(cliente_id: int):
    r = requests.get(f"{BASE_URL}/usuarios/{cliente_id}/pedidos", timeout=TIMEOUT)  # GET /usuarios/{id}/pedidos
    return comprobar_respuesta(r, 200, f"Pedidos del usuario {cliente_id[:8]}") or []


# -----------------------------------------------------------------------------
# Flujo básico de uso de la tienda
# -----------------------------------------------------------------------------
def main():
    print(f"Cliente de la Tienda Online -> API en {BASE_URL}")

    # Comprobar que la API está accesible
    try:
        requests.get(f"{BASE_URL}/docs", timeout=TIMEOUT).raise_for_status()
    except requests.RequestException as e:
        print(f"\nNo se puede conectar con la API en {BASE_URL}: {e}")
        print("¿Está el servidor arrancado (main.py) y es correcta BASE_URL?")
        sys.exit(1)

    sufijo = int(time.time())  # para que el email sea único en cada ejecución

    # 1. Crear un usuario
    titulo("1. Crear un usuario")
    usuario = crear_usuario(
        nombre="Marta Cliente",
        email=f"marta{sufijo}@correo.com",
        tipo="cliente",
        direccion_postal="Calle Real 10, Segovia",
    )
    if usuario is None:
        sys.exit(1)
    print(f"   Usuario creado: id={usuario['id']}, nombre={usuario['nombre']}, email={usuario['email']}")

    # 2. Consultar la lista de usuarios
    titulo("2. Lista de usuarios")
    for u in listar_usuarios():
        rol = "Administrador" if u["es_admin"] else "Cliente"
        print(f"   [{u['id'][:8]}] {u['nombre']:<20} {u['email']:<28} {rol}")

    # 3. Crear uno o varios productos
    titulo("3. Crear productos")
    nuevos = [
        crear_producto(tipo="electronico", nombre="Teclado mecánico", precio=79.99, stock=20, meses_garantia=24),
        crear_producto(tipo="ropa", nombre="Pantalón vaquero", precio=39.95, stock=12, talla="40", color="Azul"),
        crear_producto(tipo="generico", nombre="Libreta A5", precio=3.50, stock=100),
    ]
    nuevos = [p for p in nuevos if p]
    for p in nuevos:
        print(f"   Producto creado: id={p['id'][:8]} {p['nombre']} ({p['tipo']}) - {p['precio']:.2f} €")

    # Prueba de validación: un producto de ropa sin talla ni color -> 422
    print("   Prueba de error (ropa sin talla/color):")
    r = requests.post(f"{BASE_URL}/productos", json={"tipo": "ropa", "nombre": "X", "precio": 1, "stock": 1}, timeout=TIMEOUT)
    comprobar_respuesta(r, 422, "Crear producto no válido (se espera 422)")

    # 4. Consultar la lista de productos
    titulo("4. Lista de productos")
    for p in listar_productos():
        extra = ""
        if p["tipo"] == "electronico":
            extra = f"garantía {p['meses_garantia']} meses"
        elif p["tipo"] == "ropa":
            extra = f"talla {p['talla']}, {p['color']}"
        print(f"   [{p['id'][:8]}] {p['nombre']:<26} {p['precio']:>8.2f} €  stock {p['stock']:>3}  {extra}")

    # 5. Crear un pedido para el usuario
    titulo("5. Crear un pedido")
    if len(nuevos) >= 2:
        items = [
            {"producto_id": nuevos[0]["id"], "cantidad": 1},
            {"producto_id": nuevos[1]["id"], "cantidad": 2},
        ]
        pedido = crear_pedido(usuario["id"], items)
        if pedido:
            print(f"   Pedido {pedido['id'][:8]} creado. Total: {pedido['total']:.2f} €")

    # Prueba de error: pedir más stock del disponible -> 409
    print("   Prueba de error (stock insuficiente):")
    r = requests.post(
        f"{BASE_URL}/pedidos",
        json={"cliente_id": usuario["id"], "items": [{"producto_id": nuevos[0]["id"], "cantidad": 9999}]},
        timeout=TIMEOUT,
    )
    comprobar_respuesta(r, 409, "Pedido sin stock (se espera 409)")

    # 6. Consultar los pedidos del usuario
    titulo(f"6. Pedidos del usuario {usuario['nombre']}")
    for ped in pedidos_de_usuario(usuario["id"]):
        print(f"   Pedido {ped['id'][:8]} - {ped['fecha'][:19].replace('T', ' ')} - Total {ped['total']:.2f} €")
        for item in ped["items"]:
            print(f"      {item['cantidad']} x {item['nombre']:<22} {item['subtotal']:>8.2f} €")

    # Prueba de error: usuario inexistente -> 404
    print()
    r = requests.get(f"{BASE_URL}/usuarios/no-existe", timeout=TIMEOUT)
    comprobar_respuesta(r, 404, "Usuario inexistente (se espera 404)")

    print("\nFlujo completado.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1].rstrip("/")
    main()
