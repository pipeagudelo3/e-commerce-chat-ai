from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

# Este archivo define los Data Transfer Objects (DTOs),
# que se usan para validar y estructurar los datos que entran o salen
# de la API (entradas de usuario, respuestas del chat, productos, etc.)

class ProductDTO(BaseModel):
    # Representa la estructura de datos de un producto en la API.
    # Incluye validaciones para precio y stock.

    id: Optional[int] = None
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str = ""

    # Valida que el precio sea mayor que cero.
    @validator("price")
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError("price debe ser > 0")
        return v

    # Valida que el stock no sea negativo.
    @validator("stock")
    def stock_non_negative(cls, v):
        if v < 0:
            raise ValueError("stock no puede ser negativo")
        return v

    # Configuración para permitir la conversión desde modelos ORM.
    class Config:
        from_attributes = True


class ChatMessageRequestDTO(BaseModel):
    # Define el formato esperado del mensaje enviado por el usuario al chat.
    # Incluye validaciones para evitar cadenas vacías.

    session_id: str
    message: str

    # Valida que el session_id no esté vacío.
    @validator("session_id")
    def sid_not_empty(cls, v):
        if not v.strip():
            raise ValueError("session_id vacío")
        return v

    # Valida que el mensaje no esté vacío.
    @validator("message")
    def msg_not_empty(cls, v):
        if not v.strip():
            raise ValueError("message vacío")
        return v


class ChatMessageResponseDTO(BaseModel):
    # Define la estructura de respuesta del asistente al usuario.
    # Incluye los mensajes y el timestamp de generación.

    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime


class ChatHistoryDTO(BaseModel):
    # Representa un mensaje individual dentro del historial del chat.

    id: int
    role: str
    message: str
    timestamp: datetime

    # Permite construir el DTO directamente desde modelos ORM.
    class Config:
        from_attributes = True
