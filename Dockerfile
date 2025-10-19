# -------------------------------------------------------------
# Archivo: Dockerfile
# -------------------------------------------------------------
# Contenedor para ejecutar la aplicación E-commerce Chat AI
# -------------------------------------------------------------
# Basado en una imagen oficial de Python ligera y segura.
# Se usa "python:3.11-slim" para reducir el tamaño final del contenedor.
# -------------------------------------------------------------
FROM python:3.11-slim

# -------------------------------------------------------------
# Variables de entorno del contenedor
# -------------------------------------------------------------
# PYTHONDONTWRITEBYTECODE=1 → evita la creación de archivos .pyc
# PYTHONUNBUFFERED=1 → fuerza la salida sin buffer (útil para logs)
# PIP_NO_CACHE_DIR=1 → evita guardar caché de pip, reduciendo peso
# PYTHONPATH=/app → establece el directorio raíz de la aplicación
# -------------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

# -------------------------------------------------------------
# Define el directorio de trabajo dentro del contenedor
# -------------------------------------------------------------
WORKDIR /app

# -------------------------------------------------------------
# Copia el archivo de dependencias y las instala
# -------------------------------------------------------------
# Se usa instalación manual en lugar de requirements.txt
# para mantener un entorno limpio y controlado.
# -------------------------------------------------------------
COPY pyproject.toml ./
RUN pip install --upgrade pip \
 && pip install "fastapi==0.115.5" "uvicorn[standard]==0.32.0" \
    "sqlalchemy==2.0.36" "pydantic==2.9.2" "python-dotenv==1.0.1" \
    "google-generativeai==0.8.3"

# -------------------------------------------------------------
# Copia solo el código fuente del proyecto
# -------------------------------------------------------------
COPY src ./src

# -------------------------------------------------------------
# Crea el directorio donde se guardará la base de datos SQLite
# -------------------------------------------------------------
RUN mkdir -p /app/data

# -------------------------------------------------------------
# Crea un usuario no-root para mejorar la seguridad del contenedor
# -------------------------------------------------------------
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# -------------------------------------------------------------
# Expone el puerto 8000 (donde correrá FastAPI)
# -------------------------------------------------------------
EXPOSE 8000

# -------------------------------------------------------------
# Comando de inicio del contenedor
# -------------------------------------------------------------
# Uvicorn ejecuta la aplicación principal:
# - src.infrastructure.api.main:app → módulo principal FastAPI
# - host 0.0.0.0 → accesible desde fuera del contenedor
# - port 8000 → puerto de servicio por defecto
# -------------------------------------------------------------
CMD ["uvicorn", "src.infrastructure.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
