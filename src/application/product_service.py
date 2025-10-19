from typing import List
from .dtos import ProductDTO
from src.domain.repositories import IProductRepository
from src.domain.exceptions import ProductNotFoundError

class ProductService:
    def __init__(self, repo: IProductRepository):
        self.repo = repo

    def get_all_products(self) -> List[ProductDTO]:
        return [ProductDTO.model_validate(p) for p in self.repo.get_all()]

    def get_product_by_id(self, product_id: int) -> ProductDTO:
        p = self.repo.get_by_id(product_id)
        if not p:
            raise ProductNotFoundError(f"Producto {product_id} no encontrado")
        return ProductDTO.model_validate(p)
