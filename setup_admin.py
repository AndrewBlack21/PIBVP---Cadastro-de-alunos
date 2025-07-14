# setup_admin.py
from app.database import GerenciadorAlunos
import os

DB_PATH = os.path.join("data", "academia.db")
db_manager = GerenciadorAlunos(DB_PATH)

print("--- Cadastro do Usuário Administrador Principal ---")
db_manager.criar_tabelas()

if db_manager.verificar_se_existem_usuarios():
    print("❌ Um usuário administrador já existe. Este script só pode ser executado uma vez.")
    exit()

username = input("Digite um nome de usuário para o administrador: ")
password = input(f"Digite uma senha para o usuário '{username}': ")

# Cria o usuário com o papel 'admin'
success = db_manager.criar_usuario(username, password, role='admin')

if success:
    print(f"\n✅ Administrador '{username}' criado com sucesso!")
else:
    print("\n❌ Falha ao criar administrador.")