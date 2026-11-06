"""Esquemas Pydantic de la API (mismo patrón que schemas.py del profesor).

- Los esquemas *Create* describen los datos que el cliente envía (peticiones).
- Los esquemas *Read* describen los datos que la API devuelve (respuestas).

Igual que en el ejemplo (ItemBase -> ItemCreate / Item), los campos comunes se
declaran en una clase *Base* y se heredan. `from_attributes=True` es la versión
de Pydantic 2 del `orm_mode = True` del ejemplo: permite crear la respuesta a
partir de los atributos de un objeto (Producto, Usuario...).
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


# =============================================================================
# 1.1 Usuarios
# =============================================================================
class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=1)
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class UsuarioCreate(UsuarioBase):
    tipo: Literal["cliente", "administrador"] = "cliente"
    direccion_postal: str | None = None

    @model_validator(mode="after")
    def cliente_necesita_direccion(self):
        if self.tipo == "cliente" and not self.direccion_postal:
            raise ValueError("Un cliente necesita una dirección postal")
        return self


class UsuarioRead(UsuarioBase):
    id: str
    es_admin: bool

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# 1.2 Productos
# =============================================================================
class ProductoBase(BaseModel):
    tipo: Literal["generico", "electronico", "ropa"]
    nombre: str = Field(..., min_length=1)
    precio: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    meses_garantia: int | None = Field(None, ge=0)  # solo electrónicos
    talla: str | None = None                        # solo ropa
    color: str | None = None                        # solo ropa


class ProductoCreate(ProductoBase):
    @model_validator(mode="after")
    def validar_segun_tipo(self):
        if self.tipo == "electronico" and self.meses_garantia is None:
            raise ValueError("Un producto electrónico necesita 'meses_garantia'")
        if self.tipo == "ropa" and (not self.talla or not self.color):
            raise ValueError("Un producto de ropa necesita 'talla' y 'color'")
        return self


class ProductoRead(ProductoBase):
    id: str

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# 1.3 Pedidos
# =============================================================================
class PedidoItemCreate(BaseModel):
    producto_id: str
    cantidad: int = Field(..., gt=0)


class PedidoCreate(BaseModel):
    cliente_id: str
    items: list[PedidoItemCreate] = Field(..., min_length=1)


class PedidoItemRead(BaseModel):
    producto_id: str
    nombre: str
    cantidad: int
    precio_unitario: float
    subtotal: float

    model_config = ConfigDict(from_attributes=True)


class PedidoRead(BaseModel):
    id: str
    fecha: datetime
    cliente_id: str
    cliente_nombre: str
    total: float
    items: list[PedidoItemRead]

    model_config = ConfigDict(from_attributes=True)
