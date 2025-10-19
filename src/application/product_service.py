from typing import List
from .dtos import ProductDTO
from src.domain.repositories import IProductRepository
from src.domain.exceptions import ProductNotFoundError

# Servicio de aplicación encargado de la lógica de negocio relacionada con productos.
# Se comunica con el repositorio de productos para obtener información
# y devolverla en formato de DTO (Data Transfer Object).

class ProductService:
    # Constructor del servicio de productos.
    # Recibe una instancia del repositorio de productos (IProductRepository).
    def __init__(self, repo: IProductRepository):
        self.repo = repo

    # Retorna una lista de todos los productos disponibles.
    # Convierte los objetos del repositorio a instancias de ProductDTO.
    def get_all_products(self) -> List[ProductDTO]:
        return [ProductDTO.model_validate(p) for p in self.repo.get_all()]

    # Obtiene un producto específico por su ID.
    # Si el producto no existe, lanza una excepción ProductNotFoundError.
    def get_product_by_id(self, product_id: int) -> ProductDTO:
        p = self.repo.get_by_id(product_id)
        if not p:
            raise ProductNotFoundError(f"Producto {product_id} no encontrado")
        return ProductDTO.model_validate(p)
