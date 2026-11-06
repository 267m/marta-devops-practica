"""Clases de dominio de productos: Producto, ProductoElectronico y ProductoRopa."""

import uuid


class Producto:
    """Producto genérico de la tienda (clase padre de todos los productos)."""

    tipo: str = "generico"

    def __init__(self, nombre: str, precio: float, stock: int) -> None:
        """Crea un producto. El identificador único se genera automáticamente con uuid."""
        if precio <= 0:
            raise ValueError("El precio debe ser mayor que 0")
        if stock < 0:
            raise ValueError("El stock no puede ser negativo")
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.precio: float = float(precio)
        self.stock: int = int(stock)

    def hay_stock(self, cantidad: int) -> bool:
        """Indica si hay stock suficiente para la cantidad solicitada."""
        return 0 < cantidad <= self.stock

    def actualizar_stock(self, cantidad: int) -> None:
        """Actualiza el stock: cantidad negativa para compras, positiva para reposiciones."""
        if self.stock + cantidad < 0:
            raise ValueError(
                f"Stock insuficiente para '{self.nombre}' "
                f"(disponible: {self.stock}, solicitado: {-cantidad})"
            )
        self.stock += cantidad

    def to_dict(self) -> dict:
        """Devuelve los datos del producto como diccionario."""
        return {
            "id": self.id,
            "tipo": self.tipo,
            "nombre": self.nombre,
            "precio": self.precio,
            "stock": self.stock,
        }

    def __str__(self) -> str:
        """Devuelve las características principales del producto."""
        return f"{self.nombre} - {self.precio:.2f} € (stock: {self.stock}) [id: {self.id[:8]}]"


class ProductoElectronico(Producto):
    """Producto electrónico con meses de garantía."""

    tipo: str = "electronico"

    def __init__(self, nombre: str, precio: float, stock: int, meses_garantia: int) -> None:
        """Crea un producto electrónico con sus meses de garantía."""
        super().__init__(nombre, precio, stock)
        if meses_garantia < 0:
            raise ValueError("Los meses de garantía no pueden ser negativos")
        self.meses_garantia: int = int(meses_garantia)

    def to_dict(self) -> dict:
        """Devuelve los datos del producto, incluida la garantía."""
        datos = super().to_dict()
        datos["meses_garantia"] = self.meses_garantia
        return datos

    def __str__(self) -> str:
        """Descripción del producto incluyendo la garantía."""
        return f"[Electrónica] {super().__str__()} | Garantía: {self.meses_garantia} meses"


class ProductoRopa(Producto):
    """Prenda de ropa con talla y color."""

    tipo: str = "ropa"

    def __init__(self, nombre: str, precio: float, stock: int, talla: str, color: str) -> None:
        """Crea una prenda de ropa con su talla y color."""
        super().__init__(nombre, precio, stock)
        self.talla: str = talla
        self.color: str = color

    def to_dict(self) -> dict:
        """Devuelve los datos del producto, incluidas talla y color."""
        datos = super().to_dict()
        datos["talla"] = self.talla
        datos["color"] = self.color
        return datos

    def __str__(self) -> str:
        """Descripción del producto incluyendo talla y color."""
        return f"[Ropa] {super().__str__()} | Talla: {self.talla} | Color: {self.color}"
