"""Entidades do sistema: Usuario, Familia e Entrega."""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255))  # nunca a senha pura
    perfil: Mapped[str] = mapped_column(String(20), default="voluntario")  # admin | voluntario


class Familia(Base):
    __tablename__ = "familias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome_responsavel: Mapped[str] = mapped_column(String(120), index=True)
    cpf: Mapped[str] = mapped_column(String(11), unique=True, index=True)
    telefone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    endereco: Mapped[str] = mapped_column(String(200))
    qtd_membros: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(10), default="ativa")  # ativa | inativa

    entregas: Mapped[list["Entrega"]] = relationship(back_populates="familia")


class Entrega(Base):
    __tablename__ = "entregas"
    # Regra principal também garantida no banco: uma entrega por família por mês.
    __table_args__ = (
        UniqueConstraint("familia_id", "mes_referencia", name="uq_entrega_familia_mes"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    familia_id: Mapped[int] = mapped_column(ForeignKey("familias.id"))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    data_entrega: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    mes_referencia: Mapped[str] = mapped_column(String(7))  # formato AAAA-MM

    familia: Mapped["Familia"] = relationship(back_populates="entregas")
