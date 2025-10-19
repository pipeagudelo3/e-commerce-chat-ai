from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.entities import ChatMessage
from src.domain.repositories import IChatRepository
from src.infrastructure.db.models import ChatMemoryModel

class SQLChatRepository(IChatRepository):
    def __init__(self, db: Session): self.db = db

    def _to_entity(self, m: ChatMemoryModel) -> ChatMessage:
        return ChatMessage(id=m.id, session_id=m.session_id, role=m.role, message=m.message, timestamp=m.timestamp)

    def save_message(self, message: ChatMessage) -> ChatMessage:
        m = ChatMemoryModel(session_id=message.session_id, role=message.role, message=message.message, timestamp=message.timestamp)
        self.db.add(m); self.db.commit(); self.db.refresh(m)
        return self._to_entity(m)

    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        q = self.db.query(ChatMemoryModel).filter(ChatMemoryModel.session_id == session_id).order_by(ChatMemoryModel.timestamp.asc())
        if limit: q = q.limit(limit)
        return [self._to_entity(m) for m in q.all()]

    def delete_session_history(self, session_id: str) -> int:
        q = self.db.query(ChatMemoryModel).filter(ChatMemoryModel.session_id == session_id)
        count = q.count()
        q.delete(synchronize_session=False); self.db.commit()
        return count

    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        q = (self.db.query(ChatMemoryModel)
             .filter(ChatMemoryModel.session_id == session_id)
             .order_by(ChatMemoryModel.timestamp.desc())
             .limit(count))
        result = [self._to_entity(m) for m in q.all()]
        result.reverse()
        return result
