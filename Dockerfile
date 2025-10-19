FROM python:3.11-slim

# Runtime limpio y rápido
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

WORKDIR /app

# Instala solo dependencias puras (todas tienen wheel para linux/amd64)
COPY pyproject.toml ./
RUN pip install --upgrade pip \
 && pip install "fastapi==0.115.5" "uvicorn[standard]==0.32.0" \
    "sqlalchemy==2.0.36" "pydantic==2.9.2" "python-dotenv==1.0.1" \
    "google-generativeai==0.8.3"

# Copia solo el código necesario
COPY src ./src

# Carpeta de datos (SQLite)
RUN mkdir -p /app/data

# Usuario no-root (mejor práctica)
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "src.infrastructure.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
