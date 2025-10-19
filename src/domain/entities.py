from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Product:
    id: Optional[int]
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str = ""

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("El nombre no puede estar vacío")
        if self.price <= 0:
            raise ValueError("El precio debe ser > 0")
        if self.stock < 0:
            raise ValueError("El stock no puede ser negativo")

    def is_available(self) -> bool:
        return self.stock > 0

@dataclass
class ChatMessage:
    id: Optional[int]
    session_id: str
    role: str  # 'user'|'assistant'
    message: str
    timestamp: datetime

    def __post_init__(self):
        if self.role not in {"user", "assistant"}:
            raise ValueError("role inválido")
        if not self.session_id.strip():
            raise ValueError("session_id vacío")
        if not self.message.strip():
            raise ValueError("message vacío")

@dataclass
class ChatContext:
    messages: List[ChatMessage]
    max_messages: int = 6

    def get_recent_messages(self) -> List[ChatMessage]:
        return self.messages[-self.max_messages:]

    def format_for_prompt(self) -> str:
        lines = []
        for m in self.get_recent_messages():
            who = "Usuario" if m.role == "user" else "Asistente"
            lines.append(f"{who}: {m.message}")
        return "\n".join(lines)
