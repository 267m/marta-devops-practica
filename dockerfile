# Imagen de la Tienda Online (API REST con FastAPI)

# a. Imagen base
FROM python:3.12-slim

# Python sin ficheros .pyc y con la salida por consola sin buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# b. Copia de las dependencias (se copia antes que el código para aprovechar la caché de capas)
COPY requirements.txt .

# c. Instalación de las dependencias (sin guardar la caché de pip para reducir el tamaño)
RUN pip install --no-cache-dir -r requirements.txt

# d. Copia del código fuente
COPY src/ .

# Puerto en el que escucha la API
EXPOSE 8000

# f. Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
