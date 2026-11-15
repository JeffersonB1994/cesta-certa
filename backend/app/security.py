"""Senhas com hash Argon2 e login com token JWT."""
import os
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2 import exceptions as argon_exc
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import models
from .database import get_db

# A chave real fica em variável de ambiente, nunca no código.
SECRET_KEY = os.getenv("SECRET_KEY", "chave-apenas-para-desenvolvimento")
ALGORITHM = "HS256"
EXPIRA_HORAS = 8  # um turno de trabalho

_hasher = PasswordHasher()  # Argon2id com salt aleatório
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def gerar_hash(senha: str) -> str:
    return _hasher.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        return _hasher.verify(senha_hash, senha)
    except (argon_exc.VerificationError, argon_exc.InvalidHashError):
        return False


def criar_token(usuario: models.Usuario) -> str:
    expira = datetime.now(timezone.utc) + timedelta(hours=EXPIRA_HORAS)
    payload = {"sub": str(usuario.id), "perfil": usuario.perfil, "exp": expira}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def usuario_atual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.Usuario:
    erro = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão inválida. Faça login novamente.")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario = db.get(models.Usuario, int(payload["sub"]))
    except (jwt.PyJWTError, KeyError, ValueError):
        raise erro
    if usuario is None:
        raise erro
    return usuario


def exigir_admin(usuario: models.Usuario = Depends(usuario_atual)) -> models.Usuario:
    if usuario.perfil != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado.")
    return usuario
