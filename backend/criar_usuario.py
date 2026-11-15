"""Cria um usuário pelo terminal.

Uso: python criar_usuario.py "Nome" email@exemplo.com admin
     python criar_usuario.py "Nome" email@exemplo.com voluntario
A senha é pedida no terminal e salva apenas como hash Argon2.
"""
import getpass
import sys

from app.database import Base, SessionLocal, engine
from app.models import Usuario
from app.security import gerar_hash

if len(sys.argv) != 4 or sys.argv[3] not in ("admin", "voluntario"):
    print(__doc__)
    sys.exit(1)

nome, email, perfil = sys.argv[1], sys.argv[2], sys.argv[3]
senha = getpass.getpass("Senha (mínimo 8 caracteres): ")
if len(senha) < 8:
    print("A senha precisa ter pelo menos 8 caracteres.")
    sys.exit(1)

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    db.add(Usuario(nome=nome, email=email, senha_hash=gerar_hash(senha), perfil=perfil))
    db.commit()
print(f"Usuário {email} criado com perfil {perfil}.")
