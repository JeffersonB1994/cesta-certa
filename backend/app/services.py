"""Regras de negócio do Cesta Certa."""
from datetime import datetime
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import Entrega, Familia


class EntregaDuplicadaError(Exception):
    """A família já recebeu a cesta no mês."""


class FamiliaNaoEncontradaError(Exception):
    """A família não existe ou está inativa."""


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


def registrar_entrega(db: Session, familia_id: int, usuario_id: int, data: Optional[datetime] = None) -> Entrega:
    """Registra a entrega, permitindo só uma cesta por família por mês."""
    familia = db.get(Familia, familia_id)
    if familia is None or familia.status != "ativa":
        raise FamiliaNaoEncontradaError()

    data = data or datetime.now()
    mes = mes_referencia(data)
    if ja_recebeu_no_mes(db, familia_id, mes):
        raise EntregaDuplicadaError()

    entrega = Entrega(familia_id=familia_id, usuario_id=usuario_id, data_entrega=data, mes_referencia=mes)
    db.add(entrega)
    try:
        db.commit()
    except IntegrityError:  # dois voluntários confirmando ao mesmo tempo
        db.rollback()
        raise EntregaDuplicadaError()
    db.refresh(entrega)
    return entrega
