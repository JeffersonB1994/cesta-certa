"""Testes unitários das regras de negócio."""
from datetime import datetime

import pytest

from app import services
from app.security import gerar_hash, verificar_senha


def test_primeira_entrega_do_mes_e_registrada(db, familia, voluntario):
    entrega = services.registrar_entrega(db, familia.id, voluntario.id, datetime(2026, 11, 5))
    assert entrega.id is not None
    assert entrega.mes_referencia == "2026-11"


def test_segunda_entrega_no_mesmo_mes_e_bloqueada(db, familia, voluntario):
    services.registrar_entrega(db, familia.id, voluntario.id, datetime(2026, 11, 5))
    with pytest.raises(services.EntregaDuplicadaError):
        services.registrar_entrega(db, familia.id, voluntario.id, datetime(2026, 11, 20))


def test_entrega_no_mes_seguinte_e_permitida(db, familia, voluntario):
    services.registrar_entrega(db, familia.id, voluntario.id, datetime(2026, 11, 5))
    entrega = services.registrar_entrega(db, familia.id, voluntario.id, datetime(2026, 12, 3))
    assert entrega.mes_referencia == "2026-12"


def test_familia_inativa_nao_recebe(db, familia, voluntario):
    familia.status = "inativa"
    db.commit()
    with pytest.raises(services.FamiliaNaoEncontradaError):
        services.registrar_entrega(db, familia.id, voluntario.id)


def test_mascarar_cpf():
    assert services.mascarar_cpf("12345678900") == "123.***.***-00"


def test_senha_salva_como_hash():
    senha_hash = gerar_hash("minha-senha-123")
    assert senha_hash != "minha-senha-123"
    assert senha_hash.startswith("$argon2id$")
    assert verificar_senha("minha-senha-123", senha_hash)
    assert not verificar_senha("senha-errada", senha_hash)
