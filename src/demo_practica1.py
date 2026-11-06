"""Prueba por consola de la Práctica 1 (antiguo main.py de la P1).

En la Práctica 3, main.py pasa a ser el punto de entrada de la API REST, así que
la prueba manual por consola de la P1 se conserva en este archivo.

Ejecutar:  python demo_practica1.py   (no necesita FastAPI, solo Python)
"""

from models import Producto, ProductoElectronico, ProductoRopa
from Services import StockInsuficienteError, TiendaService


def separador(titulo: str) -> None:
    """Imprime un título de sección."""
    print("\n" + "=" * 70)
    print(titulo)
    print("=" * 70)


def mostrar_inventario(tienda: TiendaService) -> None:
    """Muestra todos los productos de la tienda."""
    for producto in tienda.listar_productos():
        print(f"  - {producto}")


def main() -> None:
    """Prueba manual del funcionamiento del sistema."""
    tienda = TiendaService()

    # 1. Registrar al menos tres clientes y un administrador
    separador("1. Registro de usuarios")
    admin = tienda.registrar_usuario("administrador", "Admin Tienda", "admin@tienda.com")
    ana = tienda.registrar_usuario("cliente", "Ana García", "ana@correo.com", "Calle Mayor 1, Madrid")
    luis = tienda.registrar_usuario("cliente", "Luis Pérez", "luis@correo.com", "Av. de la Paz 23, Segovia")
    carmen = tienda.registrar_usuario("cliente", "Carmen Ruiz", "carmen@correo.com", "Plaza España 5, Sevilla")
    for usuario in tienda.listar_usuarios():
        print(f"  - {usuario}  (is_admin: {usuario.is_admin()})")

    # 2. Crear cinco productos de diferentes categorías y añadirlos al inventario
    separador("2. Alta de productos en el inventario")
    portatil = tienda.anadir_producto(ProductoElectronico("Portátil 14\"", 899.99, 10, meses_garantia=24))
    auriculares = tienda.anadir_producto(ProductoElectronico("Auriculares inalámbricos", 59.90, 25, meses_garantia=12))
    camiseta = tienda.anadir_producto(ProductoRopa("Camiseta básica", 14.95, 40, talla="M", color="Blanco"))
    sudadera = tienda.anadir_producto(ProductoRopa("Sudadera con capucha", 34.50, 15, talla="L", color="Azul marino"))
    taza = tienda.anadir_producto(Producto("Taza de cerámica", 7.50, 30))
    print("  5 productos añadidos.")

    # 3. Listar productos para comprobar el inventario
    separador("3. Listado de productos")
    mostrar_inventario(tienda)

    # 4. Simular tres pedidos de distintos clientes con varios productos
    separador("4. Pedidos")
    pedido1 = tienda.realizar_pedido(ana.id, [(portatil.id, 1), (auriculares.id, 2)])
    print(pedido1, end="\n\n")
    pedido2 = tienda.realizar_pedido(luis.id, [(camiseta.id, 3), (sudadera.id, 1), (taza.id, 2)])
    print(pedido2, end="\n\n")
    pedido3 = tienda.realizar_pedido(carmen.id, [(auriculares.id, 1), (taza.id, 4)])
    print(pedido3, end="\n\n")
    pedido4 = tienda.realizar_pedido(ana.id, [(camiseta.id, 2), (taza.id, 1)])
    print(pedido4)

    # Comprobaciones de error: sin stock y usuario no cliente
    print("\n  Comprobación de errores:")
    try:
        tienda.realizar_pedido(luis.id, [(portatil.id, 100)])
    except StockInsuficienteError as e:
        print(f"  [OK] Pedido rechazado: {e}")
    try:
        tienda.realizar_pedido(admin.id, [(taza.id, 1)])
    except Exception as e:
        print(f"  [OK] Pedido rechazado: {e}")

    # 5. Histórico de pedidos de un cliente (ordenado por fecha)
    separador(f"5. Histórico de pedidos de {ana.nombre}")
    for pedido in tienda.listar_pedidos_usuario(ana.id):
        print(pedido, end="\n\n")

    # 6. Stock actualizado
    separador("6. Stock actualizado tras los pedidos")
    mostrar_inventario(tienda)

    # Reposición de stock y eliminación de un producto
    separador("7. Reposición y eliminación")
    print(f"  Hay stock de 5 portátiles: {portatil.hay_stock(5)}")
    portatil.actualizar_stock(5)
    print(f"  Reposición de 5 portátiles -> {portatil}")
    tienda.eliminar_producto(taza.id)
    print("  Producto 'Taza de cerámica' eliminado. Inventario final:")
    mostrar_inventario(tienda)


if __name__ == "__main__":
    main()
