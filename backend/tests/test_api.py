"""Testes de integração: API + regras + banco."""

FAMILIA = {
    "nome_responsavel": "Ana Pereira",
    "cpf": "123.456.789-00",
    "endereco": "Rua Fictícia, 100",
    "qtd_membros": 4,
}


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_pagina_inicial_abre(client):
    resposta = client.get("/")
    assert resposta.status_code == 200
    assert "Cesta Certa" in resposta.text


def test_login_com_senha_errada(client, voluntario):
    resposta = client.post("/auth/login", data={"username": voluntario.email, "password": "errada"})
    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "E-mail ou senha inválidos"


def test_login_bloqueado_apos_5_tentativas_erradas(client, voluntario):
    for _ in range(5):
        client.post("/auth/login", data={"username": voluntario.email, "password": "errada"})
    resposta = client.post("/auth/login", data={"username": voluntario.email, "password": "senha-de-teste-123"})
    assert resposta.status_code == 429
    assert "15 minutos" in resposta.json()["detail"]


def test_rota_protegida_sem_login(client):
    assert client.get("/familias", params={"busca": "Ana"}).status_code == 401


def test_cadastrar_familia_e_bloquear_cpf_repetido(client, auth):
    resposta = client.post("/familias", json=FAMILIA, headers=auth)
    assert resposta.status_code == 201
    assert resposta.json()["cpf_mascarado"] == "123.***.***-00"

    repetida = client.post("/familias", json=FAMILIA, headers=auth)
    assert repetida.status_code == 409
    assert repetida.json()["detail"] == "CPF já cadastrado"


def test_cpf_invalido_e_recusado(client, auth):
    resposta = client.post("/familias", json={**FAMILIA, "cpf": "123"}, headers=auth)
    assert resposta.status_code == 422


def test_fluxo_completo_de_entrega(client, auth):
    familia_id = client.post("/familias", json=FAMILIA, headers=auth).json()["id"]

    busca = client.get("/familias", params={"busca": "Ana"}, headers=auth).json()
    assert busca[0]["recebeu_no_mes"] is False

    primeira = client.post("/entregas", json={"familia_id": familia_id}, headers=auth)
    assert primeira.status_code == 201

    busca = client.get("/familias", params={"busca": "12345"}, headers=auth).json()
    assert busca[0]["recebeu_no_mes"] is True

    segunda = client.post("/entregas", json={"familia_id": familia_id}, headers=auth)
    assert segunda.status_code == 409
    assert segunda.json()["detail"] == "Família já recebeu a cesta neste mês"


def test_busca_com_tentativa_de_injecao_sql(client, auth):
    client.post("/familias", json=FAMILIA, headers=auth)
    resposta = client.get("/familias", params={"busca": "' OR '1'='1"}, headers=auth)
    assert resposta.status_code == 200
    assert resposta.json() == []
