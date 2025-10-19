from fastapi import FastAPI, Depends, HTTPException, APIRouter, Path
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
import os

from dotenv import load_dotenv
import google.generativeai as genai

# Carga variables de entorno (.env)
load_dotenv()

# Infraestructura (DB)
from src.infrastructure.db.database import Base, engine, get_db
from src.infrastructure.db.init_data import load_initial_data

# Repositorios
from src.infrastructure.repositories.product_repository import SQLProductRepository
from src.infrastructure.repositories.chat_repository import SQLChatRepository

# Servicio LLM (Gemini)
from src.infrastructure.llm_providers.gemini_service import GeminiService

# Capa de aplicación
from src.application.product_service import ProductService
from src.application.chat_service import ChatService
from src.application.dtos import (
    ProductDTO,
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
    ChatHistoryDTO,
)

app = FastAPI(
    title="E-commerce Chat AI",
    version="1.0.0",
    description="API de productos + chat IA (Gemini) con arquitectura hexagonal",
)

# CORS (ajusta origins si necesitas restringir)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Eventos ----------
@app.on_event("startup")
def on_startup():
    # Crear tablas y cargar datos seed si hace falta
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        load_initial_data(db)
    finally:
        db.close()


# ---------- Endpoints base ----------
@app.get("/", tags=["root"])
def root():
    return {"name": "E-commerce Chat AI", "version": "1.0.0", "docs": "/docs"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


# ---------- Endpoints de productos ----------
@app.get("/products", response_model=List[ProductDTO], tags=["products"])
def list_products(db: Session = Depends(get_db)):
    service = ProductService(SQLProductRepository(db))
    return service.get_all_products()


@app.get("/products/{product_id}", response_model=ProductDTO, tags=["products"])
def get_product(product_id: int, db: Session = Depends(get_db)):
    service = ProductService(SQLProductRepository(db))
    try:
        return service.get_product_by_id(product_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


# ---------- Endpoints de chat ----------
@app.post("/chat", response_model=ChatMessageResponseDTO, tags=["chat"])
async def chat_endpoint(payload: ChatMessageRequestDTO, db: Session = Depends(get_db)):
    product_repo = SQLProductRepository(db)
    chat_repo = SQLChatRepository(db)
    ai = GeminiService()  # toma GOOGLE_API_KEY o GEMINI_API_KEY y elige modelo válido
    chat_service = ChatService(product_repo, chat_repo, ai)
    try:
        return await chat_service.process_message(payload)
    except Exception as e:
        # Deja el detalle para debug local si hay fallo de modelo/clave/cuota
        raise HTTPException(status_code=500, detail=f"Gemini/Chat error: {e}")


@app.get("/chat/history/{session_id}", response_model=List[ChatHistoryDTO], tags=["chat"])
def history(session_id: str, limit: int = 10, db: Session = Depends(get_db)):
    chat_repo = SQLChatRepository(db)
    items = chat_repo.get_session_history(session_id, limit)
    return [ChatHistoryDTO.model_validate(i) for i in items]


@app.delete("/chat/history/{session_id}", tags=["chat"])
def clear_history(session_id: str = Path(..., description="ID de la sesión a limpiar"),
                  db: Session = Depends(get_db)):
    chat_repo = SQLChatRepository(db)
    deleted = chat_repo.delete_session_history(session_id)
    return {"session_id": session_id, "deleted_messages": deleted}

# ---------- Endpoints de AI (herramientas) ----------
ai_router = APIRouter(prefix="/ai", tags=["ai"])


@ai_router.get("/models")
def list_models():
    """
    Lista los modelos disponibles para tu API key y los métodos soportados.
    Importante: configuramos el SDK aquí mismo antes de llamar list_models().
    """
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Falta GOOGLE_API_KEY o GEMINI_API_KEY en .env",
        )

    genai.configure(api_key=api_key)

    items = []
    for m in genai.list_models():
        items.append(
            {
                "name": m.name,  # p.ej. "models/gemini-1.5-pro"
                "supported_generation_methods": getattr(
                    m, "supported_generation_methods", []
                ),
            }
        )
    return {"available_models": items}


app.include_router(ai_router)
