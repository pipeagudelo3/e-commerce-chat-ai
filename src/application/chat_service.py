from datetime import datetime, timezone
import asyncio
from .dtos import ChatMessageRequestDTO, ChatMessageResponseDTO
from src.domain.entities import ChatMessage, ChatContext
from src.domain.repositories import IProductRepository, IChatRepository
from src.domain.exceptions import ChatServiceError

class ChatService:
    def __init__(self, product_repo: IProductRepository, chat_repo: IChatRepository, ai_service):
        self.product_repo = product_repo
        self.chat_repo = chat_repo
        self.ai_service = ai_service

    async def process_message(self, request: ChatMessageRequestDTO) -> ChatMessageResponseDTO:
        try:
            products = self.product_repo.get_all()
            history = self.chat_repo.get_recent_messages(request.session_id, 6)
            context = ChatContext(messages=history)

            # Ejecuta la llamada síncrona de Gemini en un hilo
            ai_reply = await asyncio.to_thread(
                self.ai_service.generate_response_sync,
                request.message, products, context
            )

            now = datetime.now(timezone.utc)
            u_msg = ChatMessage(None, request.session_id, "user", request.message, now)
            a_msg = ChatMessage(None, request.session_id, "assistant", ai_reply, now)
            self.chat_repo.save_message(u_msg)
            self.chat_repo.save_message(a_msg)

            return ChatMessageResponseDTO(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=ai_reply,
                timestamp=now
            )
        except Exception as e:
            # deja el mensaje para ver la causa real en la respuesta
            raise ChatServiceError(f"Gemini/Chat error: {e}") from e
