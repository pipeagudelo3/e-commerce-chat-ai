from sqlalchemy.orm import Session
from .models import ProductModel

# --------------------------------------------------------------
# Módulo: init_data.py
# --------------------------------------------------------------
# Este archivo se encarga de inicializar la base de datos con datos
# predeterminados (productos de ejemplo) la primera vez que se ejecuta
# la aplicación. Si la tabla de productos está vacía, se insertan los
# registros definidos en la lista SEED.
# --------------------------------------------------------------

# --------------------------------------------------------------
# Lista de productos iniciales (datos semilla)
# --------------------------------------------------------------
# Cada elemento del diccionario representa un producto de ejemplo
# que será cargado automáticamente en la base de datos si no existen
# productos previos.
SEED = [
    dict(
        name="Air Zoom Pegasus",
        brand="Nike",
        category="Running",
        size="42",
        color="Negro",
        price=120,
        stock=5,
        description="Amortiguación reactiva"
    ),
    dict(
        name="Ultraboost 21",
        brand="Adidas",
        category="Running",
        size="41",
        color="Blanco",
        price=150,
        stock=3,
        description="Confort premium"
    ),
    dict(
        name="Suede Classic",
        brand="Puma",
        category="Casual",
        size="40",
        color="Azul",
        price=80,
        stock=10,
        description="Estilo clásico"
    ),
]

# --------------------------------------------------------------
# Función: load_initial_data
# --------------------------------------------------------------
# Recibe una sesión de base de datos (Session) e inserta los productos
# definidos en SEED solo si la tabla está vacía.
# --------------------------------------------------------------
def load_initial_data(db: Session):
    # Verifica si ya existen productos en la tabla
    if db.query(ProductModel).count() == 0:
        # Si no hay productos, se insertan los definidos en SEED
        db.add_all([ProductModel(**p) for p in SEED])
        db.commit()  # Guarda los cambios en la base de datos
