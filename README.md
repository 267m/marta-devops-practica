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
src/
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
cd src
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0
```

- Tienda (frontend): http://localhost:8000/tienda/
- Documentación (Swagger): http://localhost:8000/docs

Cliente Python (con el servidor arrancado):

```
python cliente/cliente_tienda.py
```
