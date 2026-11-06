"""Capa de servicios de la tienda online (TiendaService).

Gestiona de forma centralizada usuarios, inventario y pedidos. Cumple el mismo
papel que crud.py en el ejemplo del profesor: main.py recibe la petición HTTP y
llama a estos métodos. Igual que crud.get_item(), los métodos de consulta
devuelven None cuando algo no existe, y es main.py quien responde con un 404.
"""

from models import (
    Administrador,
    Cliente,
    LineaPedido,
    Pedido,
    Producto,
    ProductoElectronico,
    ProductoRopa,
    Usuario,
)


class TiendaError(Exception):
    """Error base de la tienda."""


class NoEncontradoError(TiendaError):
    """El usuario o un producto del pedido no existe."""


class DatosInvalidosError(TiendaError):
    """Los datos no son válidos para la operación."""


class StockInsuficienteError(TiendaError):
    """No hay stock suficiente para completar el pedido."""


class TiendaService:
    """Intermediario entre usuarios, productos y pedidos de la tienda."""

    def __init__(self) -> None:
        """Crea la tienda con usuarios, inventario y pedidos vacíos."""
        self.usuarios: dict[str, Usuario] = {}
        self.productos: dict[str, Producto] = {}
        self.pedidos: list[Pedido] = []

    # ------------------------------------------------------------------ usuarios
    def registrar_usuario(
        self, tipo: str, nombre: str, email: str, direccion_postal: str | None = None
    ) -> Usuario:
        """Registra un usuario indicando su tipo ('cliente' o 'administrador')."""
        if any(u.email == email for u in self.usuarios.values()):
            raise DatosInvalidosError(f"Ya existe un usuario con el email {email}")
        if tipo == "cliente":
            if not direccion_postal:
                raise DatosInvalidosError("Un cliente necesita una dirección postal")
            usuario: Usuario = Cliente(nombre, email, direccion_postal)
        elif tipo == "administrador":
            usuario = Administrador(nombre, email)
        else:
            raise DatosInvalidosError(f"Tipo de usuario no válido: {tipo}")
        self.usuarios[usuario.id] = usuario
        return usuario

    def listar_usuarios(self) -> list[Usuario]:
        """Devuelve todos los usuarios registrados."""
        return list(self.usuarios.values())

    def obtener_usuario(self, usuario_id: str) -> Usuario | None:
        """Devuelve el usuario con ese id, o None si no existe."""
        return self.usuarios.get(usuario_id)

    # ----------------------------------------------------------------- productos
    def anadir_producto(self, producto: Producto) -> Producto:
        """Añade al inventario un producto de cualquier categoría."""
        self.productos[producto.id] = producto
        return producto

    def crear_producto(
        self,
        tipo: str,
        nombre: str,
        precio: float,
        stock: int,
        meses_garantia: int | None = None,
        talla: str | None = None,
        color: str | None = None,
    ) -> Producto:
        """Crea un producto de la categoría indicada y lo añade al inventario."""
        if tipo == "electronico":
            producto: Producto = ProductoElectronico(nombre, precio, stock, meses_garantia)
        elif tipo == "ropa":
            producto = ProductoRopa(nombre, precio, stock, talla, color)
        elif tipo == "generico":
            producto = Producto(nombre, precio, stock)
        else:
            raise DatosInvalidosError(f"Tipo de producto no válido: {tipo}")
        return self.anadir_producto(producto)

    def listar_productos(self) -> list[Producto]:
        """Devuelve todos los productos disponibles en la tienda."""
        return list(self.productos.values())

    def obtener_producto(self, producto_id: str) -> Producto | None:
        """Devuelve el producto con ese id, o None si no existe."""
        return self.productos.get(producto_id)

    def eliminar_producto(self, producto_id: str) -> bool:
        """Elimina un producto por su id. Devuelve False si no existía."""
        if producto_id not in self.productos:
            return False
        del self.productos[producto_id]
        return True

    # ------------------------------------------------------------------- pedidos
    def realizar_pedido(self, usuario_id: str, items: list[tuple[str, int]]) -> Pedido:
        """Realiza un pedido.

        Verifica que el usuario existe (y es cliente), que existen los productos y
        que hay stock suficiente. Si todo es correcto crea el Pedido, descuenta el
        stock del inventario y devuelve el pedido creado.
        `items` es una lista de tuplas (producto_id, cantidad).
        """
        usuario = self.obtener_usuario(usuario_id)
        if usuario is None:
            raise NoEncontradoError(f"No existe el usuario con id {usuario_id}")
        if not isinstance(usuario, Cliente):
            raise DatosInvalidosError("Solo los clientes pueden realizar pedidos")

        # Sumar cantidades si un mismo producto aparece varias veces
        cantidades: dict[str, int] = {}
        for producto_id, cantidad in items:
            cantidades[producto_id] = cantidades.get(producto_id, 0) + cantidad

        # 1) Comprobar TODOS los productos antes de modificar nada
        for producto_id, cantidad in cantidades.items():
            producto = self.obtener_producto(producto_id)
            if producto is None:
                raise NoEncontradoError(f"No existe el producto con id {producto_id}")
            if not producto.hay_stock(cantidad):
                raise StockInsuficienteError(
                    f"Stock insuficiente para '{producto.nombre}' "
                    f"(disponible: {producto.stock}, solicitado: {cantidad})"
                )

        # 2) Crear el pedido y descontar el stock
        lineas = [LineaPedido(self.productos[pid], cant) for pid, cant in cantidades.items()]
        pedido = Pedido(usuario, lineas)
        for linea in lineas:
            linea.producto.actualizar_stock(-linea.cantidad)
        self.pedidos.append(pedido)
        return pedido

    def listar_pedidos_usuario(self, usuario_id: str) -> list[Pedido]:
        """Lista los pedidos de un usuario (por su id) ordenados por fecha."""
        pedidos = [p for p in self.pedidos if p.cliente.id == usuario_id]
        return sorted(pedidos, key=lambda p: p.fecha)

    # ------------------------------------------------------------ datos de demo
    def cargar_datos_ejemplo(self) -> None:
        """Carga datos de ejemplo: 3 clientes, 1 administrador y 5 productos."""
        self.registrar_usuario("administrador", "Admin Tienda", "admin@tienda.com")
        self.registrar_usuario("cliente", "Ana García", "ana@correo.com", "Calle Mayor 1, Madrid")
        self.registrar_usuario("cliente", "Luis Pérez", "luis@correo.com", "Av. de la Paz 23, Segovia")
        self.registrar_usuario("cliente", "Carmen Ruiz", "carmen@correo.com", "Plaza España 5, Sevilla")

        self.anadir_producto(ProductoElectronico("Portátil 14\"", 899.99, 10, 24))
        self.anadir_producto(ProductoElectronico("Auriculares inalámbricos", 59.90, 25, 12))
        self.anadir_producto(ProductoRopa("Camiseta básica", 14.95, 40, "M", "Blanco"))
        self.anadir_producto(ProductoRopa("Sudadera con capucha", 34.50, 15, "L", "Azul marino"))
        self.anadir_producto(Producto("Taza de cerámica", 7.50, 30))
