# Este archivo define las excepciones personalizadas del dominio.
# Estas clases permiten manejar errores específicos de forma controlada
# y dar mensajes más claros dentro de los servicios del sistema.

class ProductNotFoundError(Exception):
    # Excepción que se lanza cuando un producto solicitado no existe en el repositorio.
    # Se usa en el ProductService.
    ...


class ChatServiceError(Exception):
    # Excepción que se lanza cuando ocurre un error en el servicio de chat.
    # Generalmente se utiliza para capturar errores de comunicación con la IA (Gemini API).
    ...
