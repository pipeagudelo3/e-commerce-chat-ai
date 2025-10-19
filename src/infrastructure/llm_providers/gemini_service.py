import os
from typing import List
import google.generativeai as genai

# --------------------------------------------------------------
# Módulo: gemini_service.py
# --------------------------------------------------------------
# Este módulo implementa la clase GeminiService, encargada de gestionar
# toda la comunicación entre la aplicación y la API de Gemini (Google).
# Contiene la configuración del modelo, la generación de respuestas y
# el formateo de los productos y el contexto de chat para el prompt.
# --------------------------------------------------------------

# Importa las entidades del dominio necesarias para construir los prompts
from src.domain.entities import Product, ChatContext


# --------------------------------------------------------------
# Clase: GeminiService
# --------------------------------------------------------------
# Gestiona la configuración del modelo Gemini y la generación de respuestas
# basadas en el mensaje del usuario, los productos disponibles y el historial
# del chat.
# --------------------------------------------------------------
class GeminiService:
    def __init__(self):
        # Obtiene la API key desde las variables de entorno (.env)
        # Se prioriza GOOGLE_API_KEY, pero también acepta GEMINI_API_KEY.
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("No se encontró la API key (GOOGLE_API_KEY o GEMINI_API_KEY).")

        # Define el modelo por defecto, con opción de sobrescribirlo mediante MODEL_NAME en .env
        self.model_name = os.getenv("MODEL_NAME", "models/gemini-2.5-pro")

        # Configura la conexión con la API de Gemini usando la clave obtenida
        genai.configure(api_key=self.api_key)

        # Inicializa el modelo generativo (se crea una instancia del modelo configurado)
        self.model = genai.GenerativeModel(self.model_name)

    # --------------------------------------------------------------
    # Método: _format_products
    # --------------------------------------------------------------
    # Convierte la lista de productos (entidades del dominio) en un texto
    # legible para incluirlo dentro del prompt que se enviará al modelo Gemini.
    # --------------------------------------------------------------
    def _format_products(self, products: List[Product]) -> str:
        # Si no hay productos disponibles, retorna un texto indicativo
        if not products:
            return "(no hay productos disponibles)"

        # Genera una cadena con la información formateada de cada producto
        return "\n".join(
            f"- {p.name} | Marca:{p.brand} | Cat:{p.category} | "
            f"Talla:{p.size} | Color:{p.color} | ${p.price} | Stock:{p.stock} — {p.description or ''}"
            for p in products
        )

    # --------------------------------------------------------------
    # Método: generate_response_sync
    # --------------------------------------------------------------
    # Genera una respuesta textual del modelo Gemini basada en:
    # - El mensaje actual del usuario
    # - Los productos disponibles
    # - El historial del chat (contexto)
    #
    # Este método se ejecuta de forma síncrona dentro de un hilo separado.
    # --------------------------------------------------------------
    def generate_response_sync(
        self, user_message: str, products: List[Product], context: ChatContext
    ) -> str:

        # Convierte los productos y el historial en texto
        products_txt = self._format_products(products or [])
        history_txt = (context.format_for_prompt() if context else "") or "(sin historial)"

        # Construye el prompt que se enviará al modelo Gemini
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

        # --------------------------------------------------------------
        # Bloque principal: llamada al modelo generativo
        # --------------------------------------------------------------
        try:
            # Envía el prompt al modelo Gemini
            resp = self.model.generate_content(prompt)
        except Exception as e:
            # Maneja errores de conexión, red o modelo
            # Retorna una respuesta segura para evitar que el flujo se rompa
            return f"Lo siento, ahora mismo no pude generar respuesta ({type(e).__name__}). Intenta de nuevo."

        # --------------------------------------------------------------
        # Extracción de texto de la respuesta (manejo de distintos formatos)
        # --------------------------------------------------------------

        # 1) Camino feliz: respuesta directa en 'resp.text'
        text = getattr(resp, "text", None)
        if isinstance(text, str) and text.strip():
            return text.strip()

        # 2) Camino alternativo: buscar texto en candidates/parts
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

        # 3) Fallback final: respuesta por defecto si no hay texto válido
        return "Puedo ayudarte a elegir tenis: ¿prefieres running o casual, y cuál es tu presupuesto aproximado?"
