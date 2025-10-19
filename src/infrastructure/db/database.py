import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# --------------------------------------------------------------
# Módulo: database.py
# --------------------------------------------------------------
# Este módulo configura la conexión con la base de datos usando SQLAlchemy.
# Define el motor (engine), la sesión y la clase base para los modelos ORM.
# También carga las variables de entorno desde el archivo .env.
# --------------------------------------------------------------

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Obtiene la URL de la base de datos desde las variables de entorno.
# Si no existe, se usa por defecto una base de datos SQLite local.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/ecommerce_chat.db")

# --------------------------------------------------------------
# Configuración del motor de conexión (Engine)
# --------------------------------------------------------------
# El engine es responsable de manejar la comunicación con la base de datos.
# Para SQLite, se requiere el parámetro "check_same_thread" en False
# para permitir el acceso concurrente desde distintos hilos.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# --------------------------------------------------------------
# Configuración de la sesión (Session)
# --------------------------------------------------------------
# SessionLocal es una fábrica de sesiones que permite interactuar
# con la base de datos dentro de un contexto controlado.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --------------------------------------------------------------
# Declaración base de modelos
# --------------------------------------------------------------
# Todos los modelos de base de datos deben heredar de esta clase Base
# para que SQLAlchemy pueda mapearlos correctamente.
Base = declarative_base()

# --------------------------------------------------------------
# Dependencia de FastAPI para obtener una sesión de base de datos
# --------------------------------------------------------------
# Esta función se usa en los endpoints (con Depends) para abrir y cerrar
# una sesión automáticamente en cada solicitud HTTP.
def get_db():
    db = SessionLocal()
    try:
        yield db  # Devuelve una sesión activa de base de datos
    finally:
        db.close()  # Cierra la sesión al finalizar la solicitud
