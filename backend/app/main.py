"""API do Cesta Certa."""
from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas, security, services
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
    if security.login_bloqueado(form.username):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas. Tente novamente em 15 minutos.",
        )
    usuario = db.scalar(select(models.Usuario).where(models.Usuario.email == form.username))
    if usuario is None or not security.verificar_senha(form.password, usuario.senha_hash):
        security.registrar_falha_login(form.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos")
    security.limpar_tentativas(form.username)
    return {"access_token": security.criar_token(usuario)}


def _familia_resposta(db: Session, familia: models.Familia) -> schemas.FamiliaResposta:
    return schemas.FamiliaResposta(
        id=familia.id,
        nome_responsavel=familia.nome_responsavel,
        cpf_mascarado=services.mascarar_cpf(familia.cpf),
        status=familia.status,
        recebeu_no_mes=services.ja_recebeu_no_mes(db, familia.id, services.mes_referencia()),
    )


@app.post("/familias", response_model=schemas.FamiliaResposta, status_code=status.HTTP_201_CREATED)
def cadastrar_familia(
    dados: schemas.FamiliaCriar,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(security.usuario_atual),
):
    familia = models.Familia(**dados.model_dump())
    db.add(familia)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="CPF já cadastrado")
    db.refresh(familia)
    return _familia_resposta(db, familia)


@app.get("/familias", response_model=list[schemas.FamiliaResposta])
def buscar_familias(
    busca: str = Query(min_length=1, max_length=120),
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(security.usuario_atual),
):
    return [_familia_resposta(db, f) for f in services.buscar_familias(db, busca)]


@app.post("/entregas", response_model=schemas.EntregaResposta, status_code=status.HTTP_201_CREATED)
def registrar_entrega(
    dados: schemas.EntregaCriar,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(security.usuario_atual),
):
    try:
        entrega = services.registrar_entrega(db, dados.familia_id, usuario.id)
    except services.FamiliaNaoEncontradaError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Família não encontrada ou inativa")
    except services.EntregaDuplicadaError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Família já recebeu a cesta neste mês")
    return schemas.EntregaResposta(
        id=entrega.id,
        familia_id=entrega.familia_id,
        nome_responsavel=entrega.familia.nome_responsavel,
        data_entrega=entrega.data_entrega,
        mes_referencia=entrega.mes_referencia,
    )
