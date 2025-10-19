from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.entities import Product
from src.domain.repositories import IProductRepository
from src.infrastructure.db.models import ProductModel

class SQLProductRepository(IProductRepository):
    def __init__(self, db: Session): self.db = db

    def _to_entity(self, m: ProductModel) -> Product:
        return Product(id=m.id, name=m.name, brand=m.brand, category=m.category,
                       size=m.size, color=m.color, price=m.price, stock=m.stock, description=m.description)

    def get_all(self) -> List[Product]:
        return [self._to_entity(m) for m in self.db.query(ProductModel).all()]

    def get_by_id(self, product_id: int) -> Optional[Product]:
        m = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        return self._to_entity(m) if m else None

    def get_by_brand(self, brand: str) -> List[Product]:
        return [self._to_entity(m) for m in self.db.query(ProductModel).filter(ProductModel.brand == brand).all()]

    def get_by_category(self, category: str) -> List[Product]:
        return [self._to_entity(m) for m in self.db.query(ProductModel).filter(ProductModel.category == category).all()]

    def save(self, product: Product) -> Product:
        if product.id:
            m = self.db.query(ProductModel).get(product.id)
            for k in ("name","brand","category","size","color","price","stock","description"):
                setattr(m, k, getattr(product, k))
        else:
            m = ProductModel(**product.__dict__)
            self.db.add(m)
        self.db.commit(); self.db.refresh(m)
        return self._to_entity(m)

    def delete(self, product_id: int) -> bool:
        m = self.db.query(ProductModel).get(product_id)
        if not m: return False
        self.db.delete(m); self.db.commit()
        return True
