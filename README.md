# Cesta Certa

Sistema web simples para controle de entregas de cestas básicas da **Associação Comunitária Mãos Solidárias** (Joinville/SC).

Projeto acadêmico da disciplina de Projeto de Software, ligado ao **ODS 2 – Fome Zero** (meta 2.1).

## Problema
O controle das entregas era feito em fichas de papel, o que causava famílias recebendo duas vezes no mês, outras ficando sem e longas filas no dia da distribuição.

## O que o MVP faz
- Login de voluntários e administradores (senha com hash Argon2 e token JWT)
- Cadastro de famílias (CPF único e validado)
- Busca de famílias por nome ou CPF (CPF exibido mascarado)
- Registro de entrega com **bloqueio de duplicidade**: uma cesta por família por mês

## Tecnologias
- **Back-end:** Python + FastAPI + SQLAlchemy
- **Front-end:** Angular
- **Banco de dados:** SQLite no desenvolvimento / PostgreSQL em produção
- **Testes:** pytest
- **CI:** GitHub Actions

## Estrutura
```
cesta-certa/
├── backend/
│   ├── app/
│   │   ├── main.py        # rotas da API
│   │   ├── services.py    # regras de negócio
│   │   ├── models.py      # entidades: Usuario, Familia, Entrega
│   │   ├── schemas.py     # validação de entrada e saída
│   │   ├── security.py    # hash de senha e JWT
│   │   └── database.py    # conexão com o banco
│   ├── tests/             # testes unitários e de integração
│   └── criar_usuario.py   # cria usuários pelo terminal
├── frontend/              # telas em Angular
└── docs/
```

## Como rodar o back-end
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate | Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
python criar_usuario.py "Seu Nome" voce@exemplo.com admin
uvicorn app.main:app --reload
```
Acesse http://127.0.0.1:8000/docs para testar a API (botão **Authorize** para fazer login).

## Como rodar os testes
```bash
cd backend
pytest -v
pytest --cov=app   # com relatório de cobertura
```

## Rotas principais
| Método | Rota | O que faz |
|---|---|---|
| POST | /auth/login | Login e geração do token |
| POST | /familias | Cadastra uma família |
| GET | /familias?busca= | Busca por nome ou CPF |
| POST | /entregas | Registra a entrega (bloqueia duplicidade no mês) |

## Variáveis de ambiente
- `DATABASE_URL` – endereço do banco (padrão: SQLite local)
- `SECRET_KEY` – chave de assinatura do token (obrigatória em produção)

## Status
🚧 Em desenvolvimento – MVP.
