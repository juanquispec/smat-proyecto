from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt

# Importamos nuestros módulos locales
import models
import schemas
from database import engine, get_db

# 1. CREACIÓN DE TABLAS (Heredado del Lab 3)
models.Base.metadata.create_all(bind=engine)

# 2. METADATOS SWAGGER (Lab 4.2)
app = FastAPI(
    title="SMAT - Sistema de Monitoreo de Alerta Temprana",
    description="""
    API robusta para la gestión y monitoreo de desastres naturales.
    Permite la telemetría de sensores en tiempo real y el cálculo de niveles de riesgo.
    
    **Entidades principales:**
    * **Estaciones:** Puntos de monitoreo físico.
    * **Lecturas:** Datos capturados por sensores.
    """,
    version="1.0.0"
)

# 3. MIDDLEWARE CORS (Lab 4.3)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite conexiones desde Flutter/Web
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. CONFIGURACIÓN DE SEGURIDAD JWT (Lab 4.4)
SECRET_KEY = "UNMSM_secreto_super_seguro"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def obtener_identidad_actual(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ha expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Firma de token inválida")

@app.post("/token", tags=["Seguridad"])
def login_generar_token():
    """Genera un token JWT para autenticar sensores y administradores."""
    token_jwt = jwt.encode({"sub": "admin_smat"}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token_jwt, "token_type": "bearer"}


# 5. ENDPOINTS DEL NEGOCIO PROTEGIDOS

@app.post("/estaciones/", status_code=status.HTTP_201_CREATED, tags=["Gestión"])
def crear_estacion(estacion: schemas.EstacionCreate, db: Session = Depends(get_db), usuario: str = Depends(obtener_identidad_actual)):
    """Crea una nueva estación (Requiere Token JWT)"""
    db_estacion = db.query(models.Estacion).filter(models.Estacion.id == estacion.id).first()
    if db_estacion:
        raise HTTPException(status_code=400, detail="El ID de estación ya existe.")
    
    nueva_estacion = models.Estacion(id=estacion.id, nombre=estacion.nombre, ubicacion=estacion.ubicacion)
    db.add(nueva_estacion)
    db.commit()
    db.refresh(nueva_estacion)
    return {"message": "Estación creada", "data": {"id": nueva_estacion.id, "nombre": nueva_estacion.nombre}}

@app.post("/lecturas/", status_code=status.HTTP_201_CREATED, tags=["Telemetría"])
def registrar_lectura(lectura: schemas.LecturaCreate, db: Session = Depends(get_db), usuario: str = Depends(obtener_identidad_actual)):
    """Registra datos de los sensores (Requiere Token JWT)"""
    estacion_existe = db.query(models.Estacion).filter(models.Estacion.id == lectura.estacion_id).first()
    if not estacion_existe:
         raise HTTPException(status_code=404, detail="Error de Integridad: La estación no existe en la base de datos.")

    nueva_lectura = models.Lectura(estacion_id=lectura.estacion_id, valor=lectura.valor)
    db.add(nueva_lectura)
    db.commit()
    db.refresh(nueva_lectura)
    return {"message": "Lectura registrada", "data": {"estacion_id": nueva_lectura.estacion_id, "valor": nueva_lectura.valor}}

@app.get("/estaciones/", tags=["Gestión"])
def listar_estaciones(db: Session = Depends(get_db)):
    """Lista todas las estaciones disponibles (Público)"""
    return db.query(models.Estacion).all()

@app.get("/estaciones/{id}/riesgo", tags=["Reportes Históricos"])
def evaluar_riesgo(id: int, db: Session = Depends(get_db)):
    """Calcula el riesgo en base a la última lectura (Público)"""
    estacion = db.query(models.Estacion).filter(models.Estacion.id == id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")

    ultima_lectura = db.query(models.Lectura).filter(models.Lectura.estacion_id == id).order_by(models.Lectura.id.desc()).first()
    if not ultima_lectura:
        raise HTTPException(status_code=400, detail="La estación no tiene lecturas registradas")

    valor = ultima_lectura.valor
    nivel = "PELIGRO" if valor > 50.0 else "ALERTA" if valor > 20.0 else "NORMAL"
    return {"id": id, "valor": valor, "nivel": nivel}

@app.get("/estaciones/{id}/historial", tags=["Reportes Históricos"])
def obtener_historial(id: int, db: Session = Depends(get_db)):
    """Devuelve historial estadístico de una estación (Público)"""
    estacion = db.query(models.Estacion).filter(models.Estacion.id == id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")

    lecturas_db = db.query(models.Lectura).filter(models.Lectura.estacion_id == id).all()
    valores_lecturas = [l.valor for l in lecturas_db]
    conteo = len(valores_lecturas)
    promedio = sum(valores_lecturas) / conteo if conteo > 0 else 0.0

    return {
        "estacion_id": id,
        "lecturas": valores_lecturas,
        "conteo": conteo,
        "promedio": round(promedio, 2)
    }