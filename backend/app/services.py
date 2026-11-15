"""Regras de negócio do Cesta Certa."""
from datetime import datetime
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .models import Entrega, Familia


def mascarar_cpf(cpf: str) -> str:
    """Mostra só o começo e o fim do CPF: 123.***.***-00."""
    return f"{cpf[:3]}.***.***-{cpf[-2:]}"


def mes_referencia(data: Optional[datetime] = None) -> str:
    return (data or datetime.now()).strftime("%Y-%m")


def buscar_familias(db: Session, termo: str) -> list[Familia]:
    """Busca por parte do nome ou pelo início do CPF (consulta parametrizada pelo ORM)."""
    termo = termo.strip()
    condicoes = [Familia.nome_responsavel.ilike(f"%{termo}%")]
    numeros = "".join(c for c in termo if c.isdigit())
    if numeros:
        condicoes.append(Familia.cpf.startswith(numeros))
    consulta = select(Familia).where(or_(*condicoes)).order_by(Familia.nome_responsavel).limit(20)
    return list(db.scalars(consulta))


def ja_recebeu_no_mes(db: Session, familia_id: int, mes: str) -> bool:
    consulta = select(Entrega.id).where(Entrega.familia_id == familia_id, Entrega.mes_referencia == mes)
    return db.scalar(consulta) is not None
