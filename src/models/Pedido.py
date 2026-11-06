"""Clase de dominio Pedido."""

import uuid
from datetime import datetime

from .Producto import Producto
from .Usuario import Cliente


class LineaPedido:
    """Un producto del pedido con su cantidad y el precio en el momento de la compra."""

    def __init__(self, producto: Producto, cantidad: int) -> None:
        """Crea una línea de pedido."""
        self.producto: Producto = producto
        self.cantidad: int = cantidad
        self.precio_unitario: float = producto.precio

    @property
    def producto_id(self) -> str:
        """Id del producto de la línea."""
        return self.producto.id

    @property
    def nombre(self) -> str:
        """Nombre del producto de la línea."""
        return self.producto.nombre

    @property
    def subtotal(self) -> float:
        """Importe de la línea (precio x cantidad)."""
        return round(self.precio_unitario * self.cantidad, 2)


class Pedido:
    """Pedido realizado por un cliente con una lista de productos y cantidades."""

    def __init__(self, cliente: Cliente, lineas: list[LineaPedido]) -> None:
        """Crea un pedido. El id (uuid) y la fecha se generan automáticamente."""
        if not lineas:
            raise ValueError("Un pedido debe contener al menos un producto")
        self.id: str = str(uuid.uuid4())
        self.cliente: Cliente = cliente
        self.lineas: list[LineaPedido] = lineas
        self.fecha: datetime = datetime.now()

    def calcular_total(self) -> float:
        """Calcula el importe total a partir de precios y cantidades."""
        return round(sum(linea.subtotal for linea in self.lineas), 2)

    @property
    def total(self) -> float:
        """Importe total del pedido."""
        return self.calcular_total()

    @property
    def cliente_id(self) -> str:
        """Id del cliente que hizo el pedido."""
        return self.cliente.id

    @property
    def cliente_nombre(self) -> str:
        """Nombre del cliente que hizo el pedido."""
        return self.cliente.nombre

    @property
    def items(self) -> list[LineaPedido]:
        """Líneas del pedido (nombre usado por el esquema PedidoRead)."""
        return self.lineas

    def __str__(self) -> str:
        """Resumen legible del pedido: cliente, productos y total."""
        texto = f"Pedido {self.id[:8]} - {self.fecha:%d/%m/%Y %H:%M:%S} - Cliente: {self.cliente.nombre}\n"
        for linea in self.lineas:
            texto += f"   {linea.cantidad} x {linea.producto.nombre} = {linea.subtotal:.2f} €\n"
        texto += f"   TOTAL: {self.total:.2f} €"
        return texto
