"""Cria dados FICTÍCIOS para demonstração e testes de usabilidade.

Uso: python dados_demo.py
Cria o usuário voluntario@teste.com (senha: demo12345) e algumas famílias fictícias.
"""
from datetime import datetime

from app.database import Base, SessionLocal, engine
from app.models import Entrega, Familia, Usuario
from app.security import gerar_hash

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    if db.query(Usuario).filter_by(email="voluntario@teste.com").first():
        print("Dados de demonstração já existem.")
    else:
        voluntario = Usuario(nome="Voluntário Demo", email="voluntario@teste.com",
                             senha_hash=gerar_hash("demo12345"), perfil="voluntario")
        db.add(voluntario)
        familias = [
            Familia(nome_responsavel="Ana Pereira", cpf="12345678900", endereco="Rua Fictícia, 100", qtd_membros=4),
            Familia(nome_responsavel="Ana Souza da Silva", cpf="98765432111", endereco="Rua Exemplo, 25", qtd_membros=3),
            Familia(nome_responsavel="Carlos Oliveira", cpf="11122233344", endereco="Rua Modelo, 7", qtd_membros=5),
        ]
        db.add_all(familias)
        db.commit()
        # Ana Souza da Silva já recebeu neste mês (para demonstrar o bloqueio)
        agora = datetime.now()
        db.add(Entrega(familia_id=familias[1].id, usuario_id=voluntario.id,
                       data_entrega=agora, mes_referencia=agora.strftime("%Y-%m")))
        db.commit()
        print("Pronto! Login: voluntario@teste.com | Senha: demo12345")
