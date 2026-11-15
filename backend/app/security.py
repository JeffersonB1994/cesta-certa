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

MAX_TENTATIVAS = 5
BLOQUEIO_MINUTOS = 15

_hasher = PasswordHasher()  # Argon2id com salt aleatório
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def gerar_hash(senha: str) -> str:
    return _hasher.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        return _hasher.verify(senha_hash, senha)
    except (argon_exc.VerificationError, argon_exc.InvalidHashError):
        return False


# Controle simples de tentativas de login, guardado em memória.
_tentativas: dict[str, dict] = {}


def login_bloqueado(email: str) -> bool:
    """Indica se o e-mail está temporariamente bloqueado por excesso de erros."""
    registro = _tentativas.get(email.lower())
    if not registro or registro["bloqueado_ate"] is None:
        return False
    return registro["bloqueado_ate"] > datetime.now(timezone.utc)


def registrar_falha_login(email: str) -> None:
    """Conta um erro de senha e bloqueia por 15 minutos ao chegar a 5 erros."""
    registro = _tentativas.setdefault(email.lower(), {"falhas": 0, "bloqueado_ate": None})
    registro["falhas"] += 1
    if registro["falhas"] >= MAX_TENTATIVAS:
        registro["bloqueado_ate"] = datetime.now(timezone.utc) + timedelta(minutes=BLOQUEIO_MINUTOS)
        registro["falhas"] = 0


def limpar_tentativas(email: str) -> None:
    """Zera o contador depois de um login correto."""
    _tentativas.pop(email.lower(), None)


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
