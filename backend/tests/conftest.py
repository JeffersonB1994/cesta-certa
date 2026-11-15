"""Configuração dos testes: banco SQLite em memória, separado do banco real."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.database import Base, get_db
from app.main import app
from app.security import gerar_hash

SENHA_TESTE = "senha-de-teste-123"


@pytest.fixture
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    sessao = sessionmaker(bind=engine)()
    yield sessao
    sessao.close()


@pytest.fixture
def client(db):
    def _db_teste():
        yield db

    app.dependency_overrides[get_db] = _db_teste
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def voluntario(db):
    usuario = models.Usuario(
        nome="Voluntário Teste", email="voluntario@teste.com",
        senha_hash=gerar_hash(SENHA_TESTE), perfil="voluntario",
    )
    db.add(usuario)
    db.commit()
    return usuario


@pytest.fixture
def familia(db):
    familia = models.Familia(
        nome_responsavel="Ana Pereira", cpf="12345678900",
        endereco="Rua Fictícia, 100", qtd_membros=4, status="ativa",
    )
    db.add(familia)
    db.commit()
    return familia


@pytest.fixture
def auth(client, voluntario):
    resposta = client.post("/auth/login", data={"username": voluntario.email, "password": SENHA_TESTE})
    return {"Authorization": f"Bearer {resposta.json()['access_token']}"}
