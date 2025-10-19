from fastapi import FastAPI, Depends, HTTPException, APIRouter, Path
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
import os

from dotenv import load_dotenv
import google.generativeai as genai

# --------------------------------------------------------------
# Este archivo define la API principal del sistema.
# Aquí se inicializa la aplicación FastAPI, se configuran los endpoints
# y se integran los servicios, repositorios y la capa de inteligencia artificial.
# --------------------------------------------------------------

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# -------------------- Infraestructura (DB) --------------------
from src.infrastructure.db.database import Base, engine, get_db
from src.infrastructure.db.init_data import load_initial_data

# -------------------- Repositorios --------------------
from src.infrastructure.repositories.product_repository import SQLProductRepository
from src.infrastructure.repositories.chat_repository import SQLChatRepository

# -------------------- Servicio LLM (Gemini) --------------------
from src.infrastructure.llm_providers.gemini_service import GeminiService

# -------------------- Capa de Aplicación --------------------
from src.application.product_service import ProductService
from src.application.chat_service import ChatService
from src.application.dtos import (
    ProductDTO,
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
    ChatHistoryDTO,
)

# --------------------------------------------------------------
# Configuración principal de la aplicación FastAPI
# --------------------------------------------------------------
app = FastAPI(
    title="E-commerce Chat AI",
    version="1.0.0",
    description="API de productos + chat IA (Gemini) con arquitectura hexagonal",
)

# --------------------------------------------------------------
# Configuración de CORS
# (permite que la API sea consumida desde cualquier origen)
# --------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar por dominios específicos en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------
# EVENTOS DE INICIO DE LA APLICACIÓN
# --------------------------------------------------------------
@app.on_event("startup")
def on_startup():
    # Crea las tablas en la base de datos y carga los datos iniciales (seed)
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        load_initial_data(db)
    finally:
        db.close()


# --------------------------------------------------------------
# ENDPOINTS BÁSICOS
# --------------------------------------------------------------
@app.get("/", tags=["root"])
def root():
    # Retorna información general sobre el servicio
    return {"name": "E-commerce Chat AI", "version": "1.0.0", "docs": "/docs"}


@app.get("/health", tags=["health"])
def health():
    # Endpoint de prueba para verificar que la API está viva
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


# --------------------------------------------------------------
# ENDPOINTS DE PRODUCTOS
# --------------------------------------------------------------
@app.get("/products", response_model=List[ProductDTO], tags=["products"])
def list_products(db: Session = Depends(get_db)):
    # Retorna la lista completa de productos desde el repositorio SQL
    service = ProductService(SQLProductRepository(db))
    return service.get_all_products()


@app.get("/products/{product_id}", response_model=ProductDTO, tags=["products"])
def get_product(product_id: int, db: Session = Depends(get_db)):
    # Retorna un producto específico según su ID
    service = ProductService(SQLProductRepository(db))
    try:
        return service.get_product_by_id(product_id)
    except Exception as e:
        # Si no se encuentra el producto, devuelve error 404
        raise HTTPException(status_code=404, detail=str(e))


# --------------------------------------------------------------
# ENDPOINTS DE CHAT CON IA
# --------------------------------------------------------------
@app.post("/chat", response_model=ChatMessageResponseDTO, tags=["chat"])
async def chat_endpoint(payload: ChatMessageRequestDTO, db: Session = Depends(get_db)):
    # Procesa un mensaje enviado por el usuario al asistente IA (Gemini)
    product_repo = SQLProductRepository(db)
    chat_repo = SQLChatRepository(db)
    ai = GeminiService()  # Toma la clave API de GEMINI_API_KEY o GOOGLE_API_KEY
    chat_service = ChatService(product_repo, chat_repo, ai)

    try:
        return await chat_service.process_message(payload)
    except Exception as e:
        # Si hay un error con el modelo, la clave o la cuota, devuelve error 500
        raise HTTPException(status_code=500, detail=f"Gemini/Chat error: {e}")


@app.get("/chat/history/{session_id}", response_model=List[ChatHistoryDTO], tags=["chat"])
def history(session_id: str, limit: int = 10, db: Session = Depends(get_db)):
    # Obtiene el historial de una sesión de chat específica
    chat_repo = SQLChatRepository(db)
    items = chat_repo.get_session_history(session_id, limit)
    return [ChatHistoryDTO.model_validate(i) for i in items]


@app.delete("/chat/history/{session_id}", tags=["chat"])
def clear_history(session_id: str = Path(..., description="ID de la sesión a limpiar"),
                  db: Session = Depends(get_db)):
    # Elimina todos los mensajes asociados a una sesión de chat
    chat_repo = SQLChatRepository(db)
    deleted = chat_repo.delete_session_history(session_id)
    return {"session_id": session_id, "deleted_messages": deleted}


# --------------------------------------------------------------
# ENDPOINTS DE MODELOS DE IA (UTILIDAD)
# --------------------------------------------------------------
ai_router = APIRouter(prefix="/ai", tags=["ai"])


@ai_router.get("/models")
def list_models():
    # Lista los modelos disponibles en la cuenta de Gemini
    # junto con sus métodos de generación soportados
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Falta GOOGLE_API_KEY o GEMINI_API_KEY en .env",
        )

    # Configura la librería del SDK antes de consultar los modelos
    genai.configure(api_key=api_key)

    # Obtiene la lista de modelos disponibles para la API Key actual
    items = []
    for m in genai.list_models():
        items.append(
            {
                "name": m.name,  # Ejemplo: "models/gemini-2.5-pro"
                "supported_generation_methods": getattr(
                    m, "supported_generation_methods", []
                ),
            }
        )
    return {"available_models": items}


# Se incluye el router de IA dentro de la aplicación principal
app.include_router(ai_router)
