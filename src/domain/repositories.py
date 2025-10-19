from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Product, ChatMessage

# Este archivo define las interfaces (contratos) que deben implementar los repositorios del dominio.
# Siguiendo la arquitectura hexagonal, las interfaces permiten desacoplar la lógica de negocio
# de los detalles de infraestructura (como la base de datos o APIs externas).

# --------------------------------------------------------------
# INTERFAZ: IProductRepository
# --------------------------------------------------------------
class IProductRepository(ABC):
    # Interfaz que define las operaciones básicas que debe implementar
    # cualquier repositorio encargado de manejar productos.

    @abstractmethod
    def get_all(self) -> List[Product]:
        # Retorna una lista con todos los productos almacenados.
        ...
    
    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        # Busca un producto por su identificador único.
        # Devuelve el producto si existe o None si no se encuentra.
        ...
    
    @abstractmethod
    def get_by_brand(self, brand: str) -> List[Product]:
        # Retorna una lista de productos filtrados por marca.
        ...
    
    @abstractmethod
    def get_by_category(self, category: str) -> List[Product]:
        # Retorna una lista de productos pertenecientes a una categoría específica.
        ...
    
    @abstractmethod
    def save(self, product: Product) -> Product:
        # Guarda un nuevo producto o actualiza uno existente en la base de datos.
        ...
    
    @abstractmethod
    def delete(self, product_id: int) -> bool:
        # Elimina un producto por su ID.
        # Retorna True si la eliminación fue exitosa, False en caso contrario.
        ...


# --------------------------------------------------------------
# INTERFAZ: IChatRepository
# --------------------------------------------------------------
class IChatRepository(ABC):
    # Interfaz que define las operaciones para manejar los mensajes
    # y sesiones del historial de chat dentro del sistema.

    @abstractmethod
    def save_message(self, message: ChatMessage) -> ChatMessage:
        # Guarda un mensaje (ya sea del usuario o del asistente) en la base de datos.
        ...
    
    @abstractmethod
    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        # Obtiene el historial completo de una sesión de chat específica.
        # Si se especifica "limit", retorna solo los últimos N mensajes.
        ...
    
    @abstractmethod
    def delete_session_history(self, session_id: str) -> int:
        # Elimina todos los mensajes asociados a una sesión.
        # Devuelve la cantidad de mensajes eliminados.
        ...
    
    @abstractmethod
    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        # Retorna los últimos mensajes enviados en una sesión.
        # Se usa para mantener el contexto en las conversaciones con la IA.
        ...
