"""Tienda online - API REST con FastAPI.

Sigue el mismo esquema que el ejemplo del profesor (fast-api-uie):
    main.py              -> rutas HTTP y códigos de respuesta
    schemas.py           -> validación y formato de entrada/salida (Pydantic)
    Services/            -> TiendaService (hace el papel de crud.py)
    models/              -> clases de dominio de la Práctica 1

Formas de arrancarlo:
    1) Botón "Run" sobre este archivo (o `python main.py`): la primera vez crea
       el entorno .venv e instala requirements.txt; luego arranca el servidor y
       abre la tienda en el navegador.
    2) Como en el ejemplo del profesor, con el .venv activado:
           uvicorn main:app --reload --host 0.0.0.0

    Documentación (Swagger):  http://localhost:8000/docs
    Tienda (frontend):        http://localhost:8000/tienda/
"""

import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def preparar_entorno() -> None:
    """Crea .venv si no existe, instala requirements.txt y relanza main.py con él."""
    venv_dir = BASE_DIR / ".venv"
    if os.name == "nt":
        python_venv = venv_dir / "Scripts" / "python.exe"
    else:
        python_venv = venv_dir / "bin" / "python"

    def dependencias_ok(python: Path) -> bool:
        return subprocess.run([str(python), "-c", "import fastapi, uvicorn, requests"],
                              capture_output=True).returncode == 0

    def instalar(python: Path) -> None:
        print(">> Instalando requirements.txt en .venv (solo la primera vez)...")
        # requirements.txt está en la raíz del repositorio (carpeta padre de src/)
        requirements = BASE_DIR / "requirements.txt"
        if not requirements.exists():
            requirements = BASE_DIR.parent / "requirements.txt"
        subprocess.check_call([str(python), "-m", "pip", "install", "-r", str(requirements)])

    if Path(sys.prefix).resolve() == venv_dir.resolve():  # ya estamos dentro del .venv
        if not dependencias_ok(Path(sys.executable)):
            instalar(Path(sys.executable))
        return

    if not python_venv.exists():
        print(f">> Creando entorno virtual en {venv_dir} ...")
        subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])
    if not dependencias_ok(python_venv):
        instalar(python_venv)
    try:
        sys.exit(subprocess.call([str(python_venv), str(Path(__file__).resolve())]))
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__" and not os.environ.get("TIENDA_SIN_VENV"):
    preparar_entorno()


# =============================================================================
# Aplicación FastAPI
# =============================================================================
from fastapi import Depends, FastAPI, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import RedirectResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

import schemas  # noqa: E402
from Services import (  # noqa: E402
    DatosInvalidosError,
    NoEncontradoError,
    StockInsuficienteError,
    TiendaService,
)

app = FastAPI(title="Tienda Online API")

# Permite que el frontend (u otro equipo de la red) llame a la API desde el navegador
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Una única tienda compartida por todos los clientes (/docs, cliente Python y frontend)
tienda = TiendaService()
tienda.cargar_datos_ejemplo()


# Dependencia que entrega el servicio a cada endpoint
# (equivalente a get_db() en el ejemplo del profesor)
def get_tienda() -> TiendaService:
    return tienda


# =============================================================================
# Endpoints: Usuarios
# =============================================================================
@app.post("/usuarios", response_model=schemas.UsuarioRead, status_code=201, tags=["Usuarios"])
def crear_usuario(usuario: schemas.UsuarioCreate, servicio: TiendaService = Depends(get_tienda)):
    try:
        return servicio.registrar_usuario(
            tipo=usuario.tipo,
            nombre=usuario.nombre,
            email=usuario.email,
            direccion_postal=usuario.direccion_postal,
        )
    except DatosInvalidosError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/usuarios", response_model=list[schemas.UsuarioRead], tags=["Usuarios"])
def leer_usuarios(servicio: TiendaService = Depends(get_tienda)):
    return servicio.listar_usuarios()


@app.get("/usuarios/{usuario_id}", response_model=schemas.UsuarioRead, tags=["Usuarios"])
def leer_usuario(usuario_id: str, servicio: TiendaService = Depends(get_tienda)):
    usuario = servicio.obtener_usuario(usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


# =============================================================================
# Endpoints: Productos
# =============================================================================
@app.post("/productos", response_model=schemas.ProductoRead, status_code=201, tags=["Productos"])
def crear_producto(producto: schemas.ProductoCreate, servicio: TiendaService = Depends(get_tienda)):
    try:
        return servicio.crear_producto(
            tipo=producto.tipo,
            nombre=producto.nombre,
            precio=producto.precio,
            stock=producto.stock,
            meses_garantia=producto.meses_garantia,
            talla=producto.talla,
            color=producto.color,
        )
    except (DatosInvalidosError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/productos", response_model=list[schemas.ProductoRead], tags=["Productos"])
def leer_productos(servicio: TiendaService = Depends(get_tienda)):
    return servicio.listar_productos()


@app.get("/productos/{producto_id}", response_model=schemas.ProductoRead, tags=["Productos"])
def leer_producto(producto_id: str, servicio: TiendaService = Depends(get_tienda)):
    producto = servicio.obtener_producto(producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@app.delete("/productos/{producto_id}", tags=["Productos"])
def eliminar_producto(producto_id: str, servicio: TiendaService = Depends(get_tienda)):
    if not servicio.eliminar_producto(producto_id):
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"message": "Producto eliminado correctamente"}


# =============================================================================
# Endpoints: Pedidos
# =============================================================================
@app.post("/pedidos", response_model=schemas.PedidoRead, status_code=201, tags=["Pedidos"])
def crear_pedido(pedido: schemas.PedidoCreate, servicio: TiendaService = Depends(get_tienda)):
    try:
        return servicio.realizar_pedido(
            usuario_id=pedido.cliente_id,
            items=[(item.producto_id, item.cantidad) for item in pedido.items],
        )
    except NoEncontradoError as e:  # cliente o producto inexistente
        raise HTTPException(status_code=404, detail=str(e))
    except StockInsuficienteError as e:  # no hay stock suficiente
        raise HTTPException(status_code=409, detail=str(e))
    except DatosInvalidosError as e:  # p. ej. un administrador intenta comprar
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/usuarios/{cliente_id}/pedidos", response_model=list[schemas.PedidoRead], tags=["Pedidos"])
def leer_pedidos_usuario(cliente_id: str, servicio: TiendaService = Depends(get_tienda)):
    if servicio.obtener_usuario(cliente_id) is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return servicio.listar_pedidos_usuario(cliente_id)


# =============================================================================
# Frontend: la carpeta frontend/ se sirve como ficheros estáticos en /tienda.
# El frontend es independiente: solo se comunica con la API mediante HTTP.
# =============================================================================
app.mount("/tienda", StaticFiles(directory=BASE_DIR / "frontend", html=True), name="tienda")


@app.get("/", include_in_schema=False)
def inicio():
    return RedirectResponse(url="/tienda/")


# =============================================================================
# Arranque con el botón Run
# =============================================================================
if __name__ == "__main__":
    import socket
    import threading
    import webbrowser

    import uvicorn

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
    except OSError:
        ip_local = "127.0.0.1"
    finally:
        s.close()

    print("=" * 62)
    print("  Tienda (frontend):    http://localhost:8000/tienda/")
    print("  Documentación /docs:  http://localhost:8000/docs")
    print(f"  Desde otro equipo:    http://{ip_local}:8000   <- BASE_URL del cliente")
    print("  CTRL + C para detener el servidor")
    print("=" * 62)

    if not os.environ.get("TIENDA_SIN_NAVEGADOR"):
        threading.Timer(1.5, lambda: webbrowser.open("http://localhost:8000/tienda/")).start()

    # host="0.0.0.0": acepta conexiones de otros equipos de la red (Parte 2)
    uvicorn.run(app, host="0.0.0.0", port=8000)
