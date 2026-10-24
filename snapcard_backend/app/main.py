import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Asegurar que sys.path contenga la carpeta raíz del backend para evitar ModuleNotFoundError en Vercel
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.config import settings
from app.database import Base, engine
from app import models  # registra los modelos antes de crear tablas
from app.routers import auth, me

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)  # para desarrollo inicial
    except Exception as e:
        print(f"Error creando tablas en BD: {e}")
    yield

app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

# Permitir CORS para solicitudes de cualquier origen (Android, emuladores, web, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(me.router)

@app.get("/", tags=["Sistema"])
def root():
    return {"status": "ok", "service": settings.app_name, "docs": "/docs"}

@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok", "service": "snap-card-api"}
