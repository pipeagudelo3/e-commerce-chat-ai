# E-commerce Chat AI  
**Backend con FastAPI + Gemini API + Arquitectura Hexagonal + Docker**

Este proyecto implementa un sistema de chat inteligente para un e-commerce, donde un asistente virtual responde preguntas y recomienda productos usando inteligencia artificial (Gemini API de Google).  
El desarrollo sigue una **arquitectura hexagonal**, permitiendo separar las capas de dominio, aplicación e infraestructura para facilitar mantenimiento y escalabilidad.

---

## Tecnologías utilizadas
- **Python 3.11+**
- **FastAPI** – Framework para API REST
- **Gemini API (Google Generative AI)** – Motor de inteligencia artificial
- **SQLAlchemy + SQLite** – Persistencia de datos
- **Docker / Docker Compose** – Contenedorización del sistema
- **Uvicorn** – Servidor ASGI de alto rendimiento
- **Pydantic** – Validación de datos
- **Python-dotenv** – Manejo de variables de entorno

---

## Instalación en entorno local

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/pipeagudelo3/e-commerce-chat-ai.git
   cd e-commerce-chat-ai

2. ## Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate   # Windows

3. ## Instalar dependencias
pip install --upgrade pip
pip install -e .

4. ## Configurar variables de entorno
Crea un archivo .env en la raíz con el siguiente contenido:

GOOGLE_API_KEY=TU_API_KEY_AQUI
DATABASE_URL=sqlite:///./data/ecommerce_chat.db
ENVIRONMENT=development
MODEL_NAME=models/gemini-2.5-pro

5. ## Ejecutar el servidor
python -m uvicorn src.infrastructure.api.main:app --reload

6. ## Abrir la documentación interactiva
http://127.0.0.1:8000/docs

## Ejecución con Docker

7. ## Construir e iniciar el contenedor
Construir e iniciar el contenedor

8. ## Acceder a la API
http://localhost:8000/docs

9. ## Detener contenedor
docker compose down


## Endpoints principales

| Método   | Ruta                         | Descripción                      |
| -------- | ---------------------------- | -------------------------------- |
| `GET`    | `/`                          | Información básica del servicio  |
| `GET`    | `/health`                    | Verifica el estado de la API     |
| `GET`    | `/products`                  | Lista todos los productos        |
| `GET`    | `/products/{product_id}`     | Obtiene un producto por ID       |
| `POST`   | `/chat`                      | Envía mensaje al asistente IA    |
| `GET`    | `/chat/history/{session_id}` | Consulta historial del chat      |
| `DELETE` | `/chat/history/{session_id}` | Borra historial de una sesión    |
| `GET`    | `/ai/models`                 | Lista modelos Gemini disponibles |



## Ejemplo de uso del endpoint /chat
POST → http://127.0.0.1:8000/chat

Body JSON:
{
  "session_id": "session_1",
  "message": "Recomiéndame unos tenis Nike para correr"
}

## Variables del entorno

| Variable         | Descripción                                            |
| ---------------- | ------------------------------------------------------ |
| `GOOGLE_API_KEY` | Clave de la API de Gemini                              |
| `DATABASE_URL`   | Ruta de la base de datos SQLite                        |
| `ENVIRONMENT`    | Entorno de ejecución (`development` o `production`)    |
| `MODEL_NAME`     | Modelo de IA utilizado (`models/gemini-2.5-pro`, etc.) |


## Proyecto académico para la materia Arquitectura de Software – Universidad EAFIT
Autor: Felipe Agudelo Posada
Año: 2025
Profesor: Wilmer Ropero Castaño