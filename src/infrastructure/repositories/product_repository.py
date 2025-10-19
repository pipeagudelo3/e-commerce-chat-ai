from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.entities import Product
from src.domain.repositories import IProductRepository
from src.infrastructure.db.models import ProductModel

# --------------------------------------------------------------
# Módulo: product_repository.py
# --------------------------------------------------------------
# Este módulo implementa la clase SQLProductRepository, responsable
# de gestionar todas las operaciones de persistencia sobre los productos.
# Se comunica con la base de datos a través de SQLAlchemy.
#
# Implementa la interfaz IProductRepository definida en la capa de dominio,
# asegurando la separación de responsabilidades dentro de la arquitectura
# hexagonal.
# --------------------------------------------------------------

class SQLProductRepository(IProductRepository):
    # ----------------------------------------------------------
    # Constructor
    # ----------------------------------------------------------
    # Recibe una instancia de sesión de base de datos (Session)
    # para ejecutar las operaciones de consulta, inserción, actualización
    # y eliminación sobre la tabla "products".
    # ----------------------------------------------------------
    def __init__(self, db: Session):
        self.db = db

    # ----------------------------------------------------------
    # Método privado: _to_entity
    # ----------------------------------------------------------
    # Convierte un objeto ProductModel (modelo de base de datos)
    # en una entidad Product del dominio.
    # Esto permite desacoplar la lógica del negocio del ORM.
    # ----------------------------------------------------------
    def _to_entity(self, m: ProductModel) -> Product:
        return Product(
            id=m.id,
            name=m.name,
            brand=m.brand,
            category=m.category,
            size=m.size,
            color=m.color,
            price=m.price,
            stock=m.stock,
            description=m.description
        )

    # ----------------------------------------------------------
    # Método: get_all
    # ----------------------------------------------------------
    # Recupera todos los productos almacenados en la base de datos
    # y los convierte en entidades del dominio.
    # ----------------------------------------------------------
    def get_all(self) -> List[Product]:
        return [self._to_entity(m) for m in self.db.query(ProductModel).all()]

    # ----------------------------------------------------------
    # Método: get_by_id
    # ----------------------------------------------------------
    # Busca un producto por su ID. Si lo encuentra, lo devuelve
    # como entidad del dominio; si no, retorna None.
    # ----------------------------------------------------------
    def get_by_id(self, product_id: int) -> Optional[Product]:
        m = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        return self._to_entity(m) if m else None

    # ----------------------------------------------------------
    # Método: get_by_brand
    # ----------------------------------------------------------
    # Devuelve una lista de productos filtrados por marca.
    # ----------------------------------------------------------
    def get_by_brand(self, brand: str) -> List[Product]:
        return [
            self._to_entity(m)
            for m in self.db.query(ProductModel).filter(ProductModel.brand == brand).all()
        ]

    # ----------------------------------------------------------
    # Método: get_by_category
    # ----------------------------------------------------------
    # Devuelve una lista de productos filtrados por categoría.
    # ----------------------------------------------------------
    def get_by_category(self, category: str) -> List[Product]:
        return [
            self._to_entity(m)
            for m in self.db.query(ProductModel).filter(ProductModel.category == category).all()
        ]

    # ----------------------------------------------------------
    # Método: save
    # ----------------------------------------------------------
    # Guarda un producto en la base de datos.
    # - Si el producto ya tiene un ID, actualiza sus campos.
    # - Si no tiene ID, crea un nuevo registro.
    # Finalmente, hace commit y retorna la entidad actualizada.
    # ----------------------------------------------------------
    def save(self, product: Product) -> Product:
        if product.id:
            # Busca el producto existente
            m = self.db.query(ProductModel).get(product.id)
            # Actualiza cada campo de manera dinámica
            for k in ("name", "brand", "category", "size", "color", "price", "stock", "description"):
                setattr(m, k, getattr(product, k))
        else:
            # Crea un nuevo producto
            m = ProductModel(**product.__dict__)
            self.db.add(m)

        # Guarda los cambios
        self.db.commit()
        self.db.refresh(m)
        return self._to_entity(m)

    # ----------------------------------------------------------
    # Método: delete
    # ----------------------------------------------------------
    # Elimina un producto de la base de datos según su ID.
    # Retorna True si se eliminó correctamente o False si no se encontró.
    # ----------------------------------------------------------
    def delete(self, product_id: int) -> bool:
        m = self.db.query(ProductModel).get(product_id)
        if not m:
            return False
        self.db.delete(m)
        self.db.commit()
        return True
