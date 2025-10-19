from datetime import datetime, timezone
import asyncio
from .dtos import ChatMessageRequestDTO, ChatMessageResponseDTO
from src.domain.entities import ChatMessage, ChatContext
from src.domain.repositories import IProductRepository, IChatRepository
from src.domain.exceptions import ChatServiceError

# Servicio encargado de manejar la lógica de negocio del chat con IA.
# Se comunica con los repositorios de productos y chat, y con el servicio de IA (Gemini)
# para generar respuestas inteligentes a partir de los mensajes del usuario.

class ChatService:
    # Constructor que inicializa el servicio con los repositorios y el proveedor de IA.
    def __init__(self, product_repo: IProductRepository, chat_repo: IChatRepository, ai_service):
        self.product_repo = product_repo
        self.chat_repo = chat_repo
        self.ai_service = ai_service

    # Método principal que procesa un mensaje del usuario.
    # Obtiene el contexto del chat, llama a Gemini para obtener una respuesta,
    # guarda ambos mensajes en el historial y devuelve la respuesta al cliente.
    async def process_message(self, request: ChatMessageRequestDTO) -> ChatMessageResponseDTO:
        try:
            # Obtiene todos los productos del catálogo y el historial reciente de chat.
            products = self.product_repo.get_all()
            history = self.chat_repo.get_recent_messages(request.session_id, 6)
            context = ChatContext(messages=history)

            # Ejecuta la llamada síncrona de Gemini en un hilo separado
            ai_reply = await asyncio.to_thread(
                self.ai_service.generate_response_sync,
                request.message, products, context
            )

            # Crea los mensajes (usuario y asistente) y los guarda en la base de datos.
            now = datetime.now(timezone.utc)
            u_msg = ChatMessage(None, request.session_id, "user", request.message, now)
            a_msg = ChatMessage(None, request.session_id, "assistant", ai_reply, now)
            self.chat_repo.save_message(u_msg)
            self.chat_repo.save_message(a_msg)

            # Retorna la respuesta formateada para el cliente.
            return ChatMessageResponseDTO(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=ai_reply,
                timestamp=now
            )
        except Exception as e:
            # Manejo de errores para identificar fallas durante la generación de respuesta.
            raise ChatServiceError(f"Gemini/Chat error: {e}") from e
