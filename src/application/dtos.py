from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class ProductDTO(BaseModel):
    id: Optional[int] = None
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str = ""

    @validator("price")
    def price_positive(cls, v):
        if v <= 0: raise ValueError("price debe ser > 0")
        return v

    @validator("stock")
    def stock_non_negative(cls, v):
        if v < 0: raise ValueError("stock no puede ser negativo")
        return v

    class Config: from_attributes = True

class ChatMessageRequestDTO(BaseModel):
    session_id: str
    message: str

    @validator("session_id")
    def sid_not_empty(cls, v):
        if not v.strip(): raise ValueError("session_id vacío")
        return v

    @validator("message")
    def msg_not_empty(cls, v):
        if not v.strip(): raise ValueError("message vacío")
        return v

class ChatMessageResponseDTO(BaseModel):
    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime

class ChatHistoryDTO(BaseModel):
    id: int
    role: str
    message: str
    timestamp: datetime

    class Config: from_attributes = True
