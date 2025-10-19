from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.entities import ChatMessage
from src.domain.repositories import IChatRepository
from src.infrastructure.db.models import ChatMemoryModel

# --------------------------------------------------------------
# Módulo: chat_repository.py
# --------------------------------------------------------------
# Este módulo implementa la clase SQLChatRepository, encargada de manejar
# todas las operaciones relacionadas con los mensajes de chat en la base
# de datos SQLite mediante SQLAlchemy.
#
# Implementa la interfaz IChatRepository definida en el dominio.
# --------------------------------------------------------------

class SQLChatRepository(IChatRepository):
    # ----------------------------------------------------------
    # Constructor
    # ----------------------------------------------------------
    # Recibe una sesión de base de datos (Session) para ejecutar
    # las operaciones CRUD (crear, leer, eliminar).
    # ----------------------------------------------------------
    def __init__(self, db: Session):
        self.db = db

    # ----------------------------------------------------------
    # Método privado: _to_entity
    # ----------------------------------------------------------
    # Convierte un objeto del modelo de base de datos (ChatMemoryModel)
    # a una entidad del dominio (ChatMessage), permitiendo mantener la
    # independencia entre capas.
    # ----------------------------------------------------------
    def _to_entity(self, m: ChatMemoryModel) -> ChatMessage:
        return ChatMessage(
            id=m.id,
            session_id=m.session_id,
            role=m.role,
            message=m.message,
            timestamp=m.timestamp
        )

    # ----------------------------------------------------------
    # Método: save_message
    # ----------------------------------------------------------
    # Guarda un nuevo mensaje (usuario o asistente) en la base de datos.
    # - Convierte la entidad del dominio en un modelo SQLAlchemy.
    # - Hace commit y refresca el registro insertado.
    # ----------------------------------------------------------
    def save_message(self, message: ChatMessage) -> ChatMessage:
        m = ChatMemoryModel(
            session_id=message.session_id,
            role=message.role,
            message=message.message,
            timestamp=message.timestamp
        )
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return self._to_entity(m)

    # ----------------------------------------------------------
    # Método: get_session_history
    # ----------------------------------------------------------
    # Recupera el historial completo o limitado de una sesión específica.
    # - Los resultados se ordenan cronológicamente (más antiguos primero).
    # ----------------------------------------------------------
    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        q = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(ChatMemoryModel.timestamp.asc())
        )
        if limit:
            q = q.limit(limit)
        return [self._to_entity(m) for m in q.all()]

    # ----------------------------------------------------------
    # Método: delete_session_history
    # ----------------------------------------------------------
    # Elimina todos los mensajes asociados a una sesión específica.
    # Retorna la cantidad de mensajes eliminados.
    # ----------------------------------------------------------
    def delete_session_history(self, session_id: str) -> int:
        q = self.db.query(ChatMemoryModel).filter(ChatMemoryModel.session_id == session_id)
        count = q.count()
        q.delete(synchronize_session=False)
        self.db.commit()
        return count

    # ----------------------------------------------------------
    # Método: get_recent_messages
    # ----------------------------------------------------------
    # Recupera los mensajes más recientes de una sesión de chat.
    # - Se ordenan en orden descendente por timestamp.
    # - Se devuelven en orden cronológico (usuario → asistente).
    # ----------------------------------------------------------
    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        q = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(ChatMemoryModel.timestamp.desc())
            .limit(count)
        )
        result = [self._to_entity(m) for m in q.all()]
        result.reverse()  # Se invierte para conservar el orden lógico
        return result
