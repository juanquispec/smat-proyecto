from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Definir la URL de conexión. Usaremos SQLite local.
# check_same_thread=False es necesario para SQLite en FastAPI.
SQLALCHEMY_DATABASE_URL = "sqlite:///./smat.db"

# 2. Crear el Motor (Engine) que interactúa con la BD.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Crear la fábrica de Sesiones (SessionLocal).
# Cada instancia será una sesión de base de datos diferente.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Crear la clase Base de la cual heredarán todos los modelos de tablas.
Base = declarative_base()

# 5. Dependencia para FastAPI: Obtener la sesión de BD y cerrarla al terminar.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()