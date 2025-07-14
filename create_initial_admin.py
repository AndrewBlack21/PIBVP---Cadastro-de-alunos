# create_initial_admin.py
import os
from app.database import GerenciadorAlunos

print("--- Iniciando script de configuração do administrador ---")

# Pega as credenciais das Variáveis de Ambiente que configuraremos na Render
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

# Verifica se as variáveis foram definidas na Render
if not ADMIN_USERNAME or not ADMIN_PASSWORD:
    print("❌ ERRO: As variáveis de ambiente ADMIN_USERNAME e ADMIN_PASSWORD não foram definidas.")
    print("Por favor, configure-as no painel da Render antes de fazer o deploy.")
    # Usamos 'exit(1)' para parar o build se as variáveis não existirem
    exit(1)

# Conecta ao banco de dados
DB_PATH = os.path.join("data", "academia.db")
db_manager = GerenciadorAlunos(DB_PATH)

# Garante que todas as tabelas existam
db_manager.criar_tabelas()

# Verifica se o administrador já existe no banco de dados
print(f"Verificando se o administrador '{ADMIN_USERNAME}' já existe...")
user = db_manager.buscar_usuario_por_nome(ADMIN_USERNAME)

if user:
    print(f"✅ O administrador '{ADMIN_USERNAME}' já existe. Nenhuma ação necessária.")
else:
    print(f"O administrador '{ADMIN_USERNAME}' não foi encontrado. Criando agora...")
    # Se não existir, cria o usuário com o papel 'admin'
    success = db_manager.criar_usuario(ADMIN_USERNAME, ADMIN_PASSWORD, role='admin')
    if success:
        print(f"✅ Administrador '{ADMIN_USERNAME}' criado com sucesso!")
    else:
        print("❌ Falha ao criar o administrador.")
        exit(1)

print("--- Script de configuração finalizado com sucesso. ---")