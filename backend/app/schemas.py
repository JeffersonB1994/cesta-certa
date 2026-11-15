"""Formatos de entrada e saída da API (validados no servidor com Pydantic)."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class LoginResposta(BaseModel):
    access_token: str
    token_type: str = "bearer"


class FamiliaCriar(BaseModel):
    nome_responsavel: str = Field(min_length=3, max_length=120)
    cpf: str
    telefone: Optional[str] = Field(default=None, max_length=20)
    endereco: str = Field(min_length=3, max_length=200)
    qtd_membros: int = Field(ge=1, le=30)

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, valor: str) -> str:
        numeros = "".join(c for c in valor if c.isdigit())
        if len(numeros) != 11:
            raise ValueError("CPF deve ter 11 números")
        return numeros


class FamiliaResposta(BaseModel):
    id: int
    nome_responsavel: str
    cpf_mascarado: str
    status: str
    recebeu_no_mes: bool


class EntregaCriar(BaseModel):
    familia_id: int


class EntregaResposta(BaseModel):
    id: int
    familia_id: int
    nome_responsavel: str
    data_entrega: datetime
    mes_referencia: str
