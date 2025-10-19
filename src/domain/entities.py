from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

# Este archivo define las entidades del dominio.
# Representan los objetos principales del sistema (Producto, Mensaje y Contexto del Chat)
# con sus reglas de negocio básicas y validaciones.

@dataclass
class Product:
    # Entidad que representa un producto dentro del sistema de e-commerce.
    # Incluye validaciones para asegurar la integridad de los datos.

    id: Optional[int]
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str = ""

    # Método especial que se ejecuta después de la inicialización del dataclass.
    # Realiza validaciones de negocio para evitar valores inválidos.
    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("El nombre no puede estar vacío")
        if self.price <= 0:
            raise ValueError("El precio debe ser > 0")
        if self.stock < 0:
            raise ValueError("El stock no puede ser negativo")

    # Indica si el producto está disponible (stock mayor que 0).
    def is_available(self) -> bool:
        return self.stock > 0


@dataclass
class ChatMessage:
    # Entidad que representa un mensaje individual dentro de una sesión de chat.
    # Puede ser enviado por el usuario o por el asistente.

    id: Optional[int]
    session_id: str
    role: str  # 'user' o 'assistant'
    message: str
    timestamp: datetime

    # Valida los datos del mensaje al inicializar el objeto.
    def __post_init__(self):
        if self.role not in {"user", "assistant"}:
            raise ValueError("role inválido")
        if not self.session_id.strip():
            raise ValueError("session_id vacío")
        if not self.message.strip():
            raise ValueError("message vacío")


@dataclass
class ChatContext:
    # Entidad que almacena el contexto de una sesión de chat,
    # incluyendo los mensajes más recientes del historial.

    messages: List[ChatMessage]
    max_messages: int = 6

    # Obtiene los últimos mensajes según el número máximo definido.
    def get_recent_messages(self) -> List[ChatMessage]:
        return self.messages[-self.max_messages:]

    # Formatea los mensajes recientes en texto plano para enviarlos al modelo de IA.
    def format_for_prompt(self) -> str:
        lines = []
        for m in self.get_recent_messages():
            who = "Usuario" if m.role == "user" else "Asistente"
            lines.append(f"{who}: {m.message}")
        return "\n".join(lines)
