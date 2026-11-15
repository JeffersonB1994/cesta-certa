"""API do Cesta Certa."""
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas, security
from .database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cesta Certa API",
    description="Controle de entregas de cestas básicas – uma cesta por família por mês.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # front-end Angular em desenvolvimento
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Verifica se a API está no ar."""
    return {"status": "ok"}


@app.post("/auth/login", response_model=schemas.LoginResposta)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.scalar(select(models.Usuario).where(models.Usuario.email == form.username))
    if usuario is None or not security.verificar_senha(form.password, usuario.senha_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos")
    return {"access_token": security.criar_token(usuario)}
