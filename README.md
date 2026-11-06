# Tienda Online - API REST con FastAPI

**Autora:** Marta Gómez Zabal

**Asignatura:** Arquitectura de Software - Práctica 3 (DevOps: Git, GitHub y Docker)

## Descripción

Aplicación Python que implementa una tienda online. Partiendo de las clases de
dominio de la Práctica 1 (`Producto`, `ProductoElectronico`, `ProductoRopa`,
`Usuario`, `Cliente`, `Administrador`, `Pedido`) y de la lógica de negocio de
`TiendaService`, la funcionalidad se expone como una **API REST con FastAPI**
(Práctica 2) que permite gestionar usuarios, productos y pedidos.

El proyecto incluye además:

- Un **cliente Python** (`requests`) que consume la API solo mediante HTTP.
- Un **frontend web** sencillo que también usa la API mediante peticiones HTTP.

En esta práctica el proyecto se gestiona con Git y GitHub (ramas `feature/*`,
commits y Pull Requests) y se conteneriza con Docker.

## Estructura

```
.
├── dockerfile            -> definición de la imagen Docker
├── .dockerignore         -> ficheros excluidos de la construcción de la imagen
├── requirements.txt      -> dependencias con versiones fijadas (pip freeze)
├── README.md
└── src/
    ├── main.py               -> punto de entrada y endpoints de la API (FastAPI)
    ├── schemas.py            -> esquemas Pydantic (Create / Read)
    ├── Services/
    │   └── Tienda_service.py -> TiendaService (lógica de negocio)
    ├── models/               -> clases de dominio (Producto, Usuario, Pedido)
    ├── cliente/
    │   └── cliente_tienda.py -> cliente Python con requests
    ├── frontend/             -> frontend web (HTML + CSS + JS)
    └── demo_practica1.py     -> prueba por consola de la Práctica 1
```

## Ejecución local (sin Docker)

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cd src
uvicorn main:app --reload --host 0.0.0.0
```

- Tienda (frontend): http://localhost:8000/tienda/
- Documentación (Swagger): http://localhost:8000/docs

Cliente Python (con el servidor arrancado, desde la carpeta `src`):

```
python cliente/cliente_tienda.py
```

## Docker

La aplicación está contenerizada con el fichero `dockerfile` de la raíz:

| Paso | Instrucción |
|------|-------------|
| Imagen base | `FROM python:3.12-slim` |
| Dependencias | `COPY requirements.txt .` + `RUN pip install --no-cache-dir -r requirements.txt` |
| Código fuente | `COPY src/ .` |
| Permisos | se crea el usuario `appuser`, se le da la propiedad de `/app` (`chown`/`chmod`) y el contenedor se ejecuta con `USER appuser` |
| Arranque | `CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]` |

El fichero `.dockerignore` evita que entren en la imagen `.git`, entornos
virtuales, cachés de Python (`__pycache__`, `*.pyc`), `tests/`, etc.

Requisito: tener instalado y arrancado **Docker Desktop**. Todos los comandos se
lanzan desde la raíz del repositorio (donde está el `dockerfile`).

### 1. Construir la imagen

```
docker build -f dockerfile -t tienda-online:1.0.0 .
```

(`-f dockerfile` indica el fichero de construcción; `-t` pone nombre y etiqueta
de versión a la imagen; el `.` final es el contexto de construcción.)

Comprobar que la imagen existe:

```
docker images tienda-online
```

### 2. Ejecutar el contenedor

En primer plano (CTRL + C para pararlo; `--rm` borra el contenedor al pararlo):

```
docker run --rm -p 8000:8000 --name tienda tienda-online:1.0.0
```

En segundo plano:

```
docker run -d -p 8000:8000 --name tienda tienda-online:1.0.0
docker ps
docker logs tienda
docker stop tienda
docker rm tienda
```

Usando otro puerto del equipo (la API sigue escuchando en el 8000 dentro del contenedor):

```
docker run --rm -p 8080:8000 --name tienda tienda-online:1.0.0
```

En ese caso las URLs pasan a ser `http://localhost:8080/...`.

### 3. Variables de entorno

La imagen **no necesita ninguna variable de entorno** para funcionar y no
contiene secretos. El `dockerfile` define estas dos, propias de Python:

| Variable | Valor | Para qué sirve |
|----------|-------|----------------|
| `PYTHONDONTWRITEBYTECODE` | `1` | Python no genera ficheros `.pyc` dentro del contenedor |
| `PYTHONUNBUFFERED` | `1` | Los logs de uvicorn aparecen al momento en `docker logs` |

Las variables `TIENDA_SIN_VENV` y `TIENDA_SIN_NAVEGADOR` que lee `main.py` solo
se usan al lanzar `python main.py` en local; en el contenedor no aplican porque
se arranca directamente con `uvicorn`.

### 4. Salida esperada y pruebas

Al arrancar el contenedor se debe ver en consola:

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Con el contenedor en marcha, probar:

| Qué probar | URL / comando | Resultado esperado |
|------------|---------------|--------------------|
| Documentación Swagger | http://localhost:8000/docs | Página de Swagger con los endpoints de Usuarios, Productos y Pedidos |
| Frontend | http://localhost:8000/tienda/ | La tienda web con productos y usuarios |
| Listar productos | `GET /productos` | HTTP 200 y 5 productos de ejemplo (Portátil 14", Auriculares inalámbricos, Camiseta básica, Sudadera con capucha, Taza de cerámica) |
| Listar usuarios | `GET /usuarios` | HTTP 200 y 4 usuarios (Admin Tienda y 3 clientes) |
| Crear usuario | `POST /usuarios` | HTTP 201 y el usuario creado con su `id` |
| Producto inexistente | `GET /productos/no-existe` | HTTP 404 `{"detail":"Producto no encontrado"}` |

Ejemplos con `curl` (en PowerShell usar `curl.exe`):

```
curl.exe http://localhost:8000/productos
curl.exe http://localhost:8000/usuarios
curl.exe -X POST http://localhost:8000/usuarios -H "Content-Type: application/json" -d "{\"nombre\":\"Prueba Docker\",\"email\":\"docker@correo.com\",\"tipo\":\"cliente\",\"direccion_postal\":\"Calle Docker 1, Madrid\"}"
curl.exe http://localhost:8000/productos/no-existe
```

Salida del `POST /usuarios` (el `id` cambia en cada ejecución):

```
{"nombre":"Prueba Docker","email":"docker@correo.com","id":"95d7a525-...","es_admin":false}
```

Prueba completa con el cliente Python (fuera del contenedor, necesita `requests`
instalado en el equipo):

```
python src/cliente/cliente_tienda.py http://localhost:8000
```

Debe terminar mostrando todas las operaciones con `[OK]` y el mensaje
`Flujo completado.`:

```
[OK]    Crear usuario 'Marta Cliente' -> HTTP 201
[OK]    Listar usuarios -> HTTP 200
[OK]    Crear producto 'Teclado mecánico' -> HTTP 201
[OK]    Crear producto 'Pantalón vaquero' -> HTTP 201
[OK]    Crear producto 'Libreta A5' -> HTTP 201
[OK]    Crear producto no válido (se espera 422) -> HTTP 422
[OK]    Listar productos -> HTTP 200
[OK]    Crear pedido para el cliente ... -> HTTP 201
[OK]    Pedido sin stock (se espera 409) -> HTTP 409
[OK]    Pedidos del usuario ... -> HTTP 200
[OK]    Usuario inexistente (se espera 404) -> HTTP 404

Flujo completado.
```

### 5. Publicar la imagen en Docker Hub (push)

```
docker login
docker tag tienda-online:1.0.0 martagomez01/tienda-online:1.0.0
docker tag tienda-online:1.0.0 martagomez01/tienda-online:latest
docker push martagomez01/tienda-online:1.0.0
docker push martagomez01/tienda-online:latest
```

Imagen publicada: https://hub.docker.com/r/martagomez01/tienda-online

### 6. Descargar y ejecutar la imagen publicada (pull)

En cualquier equipo con Docker, sin necesidad del código fuente:

```
docker pull martagomez01/tienda-online:1.0.0
docker run --rm -p 8000:8000 martagomez01/tienda-online:1.0.0
```

Resumen del flujo: **build → run → test → push**.

## Flujo de trabajo con Git

- `main`: rama principal (protegida, solo recibe cambios mediante Pull Request).
- `feature/docker`: rama donde se desarrolla la contenerización.

Repositorio: https://github.com/267m/marta-devops-practica
