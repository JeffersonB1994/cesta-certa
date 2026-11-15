# Cesta Certa

Sistema web simples para controle de entregas de cestas básicas da **Associação Comunitária Mãos Solidárias** (Joinville/SC).

Projeto acadêmico da disciplina de Projeto de Software, ligado ao **ODS 2 – Fome Zero** (meta 2.1).

## Problema
O controle das entregas era feito em fichas de papel, o que causava famílias recebendo duas vezes no mês, outras ficando sem e longas filas no dia da distribuição.

## O que o MVP faz
- Login de voluntários e administradores
- Cadastro de famílias
- Busca de famílias por nome ou CPF
- Registro de entrega com **bloqueio de duplicidade**: uma cesta por família por mês

## Tecnologias
- **Back-end:** Python + FastAPI + SQLAlchemy
- **Front-end:** Angular
- **Banco de dados:** PostgreSQL (SQLite no desenvolvimento local)
- **Testes:** pytest
- **CI:** GitHub Actions

## Estrutura
```
cesta-certa/
├── backend/    # API em Python (FastAPI)
├── frontend/   # Telas em Angular
└── docs/       # Documentação do projeto
```

## Como rodar o back-end
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate | Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Acesse http://127.0.0.1:8000/docs para ver a API.

## Status
🚧 Em desenvolvimento – MVP.
