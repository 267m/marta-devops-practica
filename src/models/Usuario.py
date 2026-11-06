"""Clases de dominio de usuarios: Usuario, Cliente y Administrador."""

import uuid


class Usuario:
    """Cualquier persona que interactúa con la tienda."""

    tipo: str = "usuario"

    def __init__(self, nombre: str, email: str) -> None:
        """Crea un usuario. El identificador único se genera automáticamente con uuid."""
        self.id: str = str(uuid.uuid4())
        self.nombre: str = nombre
        self.email: str = email

    def is_admin(self) -> bool:
        """Indica si el usuario es administrador (por defecto, False)."""
        return False

    @property
    def es_admin(self) -> bool:
        """Mismo valor que is_admin(); lo usa el esquema UsuarioRead de la API."""
        return self.is_admin()

    def __str__(self) -> str:
        """Devuelve el nombre y el email del usuario."""
        return f"{self.nombre} <{self.email}> [id: {self.id[:8]}]"


class Cliente(Usuario):
    """Cliente de la tienda: puede realizar pedidos y tiene dirección postal."""

    tipo: str = "cliente"

    def __init__(self, nombre: str, email: str, direccion_postal: str) -> None:
        """Crea un cliente con su dirección postal."""
        super().__init__(nombre, email)
        self.direccion_postal: str = direccion_postal

    def __str__(self) -> str:
        """Descripción del cliente incluyendo su dirección."""
        return f"Cliente: {super().__str__()} - {self.direccion_postal}"


class Administrador(Usuario):
    """Gestor de la tienda."""

    tipo: str = "administrador"

    def is_admin(self) -> bool:
        """Un administrador siempre devuelve True."""
        return True

    def __str__(self) -> str:
        """Descripción del administrador."""
        return f"Administrador: {super().__str__()}"
