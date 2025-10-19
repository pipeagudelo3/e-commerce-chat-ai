from sqlalchemy.orm import Session
from .models import ProductModel

SEED = [
    dict(name="Air Zoom Pegasus", brand="Nike", category="Running", size="42", color="Negro", price=120, stock=5, description="Amortiguación reactiva"),
    dict(name="Ultraboost 21", brand="Adidas", category="Running", size="41", color="Blanco", price=150, stock=3, description="Confort premium"),
    dict(name="Suede Classic", brand="Puma", category="Casual", size="40", color="Azul", price=80, stock=10, description="Estilo clásico"),
]

def load_initial_data(db: Session):
    if db.query(ProductModel).count() == 0:
        db.add_all([ProductModel(**p) for p in SEED])
        db.commit()
