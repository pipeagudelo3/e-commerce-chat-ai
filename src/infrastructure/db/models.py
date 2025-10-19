from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Index
from sqlalchemy.sql import func
from .database import Base

# --------------------------------------------------------------
# Módulo: models.py
# --------------------------------------------------------------
# Este módulo define las clases ORM (Object Relational Mapping)
# que representan las tablas de la base de datos.
# Cada clase hereda de Base (definida en database.py) y define
# sus columnas, tipos de datos y restricciones.
# --------------------------------------------------------------


# --------------------------------------------------------------
# Clase: ProductModel
# --------------------------------------------------------------
# Representa la tabla "products" en la base de datos.
# Contiene la información de los productos del e-commerce.
# --------------------------------------------------------------
class ProductModel(Base):
    __tablename__ = "products"  # Nombre de la tabla en la base de datos

    # Definición de columnas
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    brand = Column(String(100), index=True)
    category = Column(String(100), index=True)
    size = Column(String(20))
    color = Column(String(50))
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    description = Column(Text, default="")

    # No se definen métodos adicionales porque esta clase actúa
    # únicamente como modelo de persistencia.


# --------------------------------------------------------------
# Clase: ChatMemoryModel
# --------------------------------------------------------------
# Representa la tabla "chat_memory" en la base de datos.
# Almacena los mensajes enviados por el usuario y las respuestas
# del asistente IA, junto con un identificador de sesión.
# --------------------------------------------------------------
class ChatMemoryModel(Base):
    __tablename__ = "chat_memory"  # Nombre de la tabla en la base de datos

    # Definición de columnas
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True, nullable=False)
    role = Column(String(20), nullable=False)  # Valores esperados: 'user' o 'assistant'
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

# --------------------------------------------------------------
# Índice compuesto: ix_chat_session_time
# --------------------------------------------------------------
# Mejora la velocidad de las consultas por sesión y orden temporal.
# Es útil para recuperar rápidamente los mensajes recientes de una sesión.
Index("ix_chat_session_time", ChatMemoryModel.session_id, ChatMemoryModel.timestamp)
