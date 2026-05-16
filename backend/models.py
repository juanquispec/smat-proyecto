from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

# 1. Modelo para la tabla 'estaciones'
class Estacion(Base):
    __tablename__ = "estaciones"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    ubicacion = Column(String)

    # Relación uno-a-muchos con Lecturas
    lecturas = relationship("Lectura", back_populates="estacion")

# 2. Modelo para la tabla 'lecturas'
class Lectura(Base):
    __tablename__ = "lecturas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    estacion_id = Column(Integer, ForeignKey("estaciones.id"))
    valor = Column(Float)

    # Relación inversa hacia Estacion
    estacion = relationship("Estacion", back_populates="lecturas")