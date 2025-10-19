import os
from typing import List
import google.generativeai as genai

# 👇 Importa desde el archivo único de entidades
from src.domain.entities import Product, ChatContext

class GeminiService:
    def __init__(self):
        # Obtiene API key desde .env (prefiere GOOGLE_API_KEY o GEMINI_API_KEY)
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("No se encontró la API key (GOOGLE_API_KEY o GEMINI_API_KEY).")

        # Modelo por defecto; puedes forzarlo con MODEL_NAME en .env
        self.model_name = os.getenv("MODEL_NAME", "models/gemini-2.5-pro")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def _format_products(self, products: List[Product]) -> str:
        """Convierte la lista de productos en texto legible para el prompt."""
        if not products:
            return "(no hay productos disponibles)"
        return "\n".join(
            f"- {p.name} | Marca:{p.brand} | Cat:{p.category} | "
            f"Talla:{p.size} | Color:{p.color} | ${p.price} | Stock:{p.stock} — {p.description or ''}"
            for p in products
        )

    def generate_response_sync(
        self, user_message: str, products: List[Product], context: ChatContext
    ) -> str:
        """Genera la respuesta del modelo Gemini de forma segura."""
        products_txt = self._format_products(products or [])
        history_txt = (context.format_for_prompt() if context else "") or "(sin historial)"

        prompt = f"""
Eres un asistente de compras para una tienda de zapatos.
Responde en español, de manera profesional, breve y amable. Usa el contexto si existe.

PRODUCTOS DISPONIBLES:
{products_txt}

HISTORIAL DE CHAT:
{history_txt}

Usuario: {user_message}
Asistente:
""".strip()

        # --- Llamada robusta al modelo ---
        try:
            resp = self.model.generate_content(prompt)
        except Exception as e:
            # Falla del SDK/red/modelo: devuelve un texto seguro (evita None)
            return f"Lo siento, ahora mismo no pude generar respuesta ({type(e).__name__}). Intenta de nuevo."

        # 1) Camino feliz
        text = getattr(resp, "text", None)
        if isinstance(text, str) and text.strip():
            return text.strip()

        # 2) Buscar texto en candidates/parts (algunas respuestas vienen así)
        try:
            cands = getattr(resp, "candidates", None) or []
            for c in cands:
                content = getattr(c, "content", None)
                parts = getattr(content, "parts", None) or []
                for p in parts:
                    ptxt = getattr(p, "text", None)
                    if isinstance(ptxt, str) and ptxt.strip():
                        return ptxt.strip()
        except Exception:
            pass

        # 3) Fallback final (evita romper validaciones)
        return "Puedo ayudarte a elegir tenis: ¿prefieres running o casual, y cuál es tu presupuesto aproximado?"
