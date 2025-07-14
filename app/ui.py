# app/ui.py

from .database import GerenciadorAlunos # O '.' indica importação relativa

def menu_principal(db_path):
    """Exibe o menu principal e gerencia a interação do usuário."""
    gerenciador = GerenciadorAlunos(db_path)

    while True:
        print("\n===== Sistema de Controle de Alunos =====")
        print("1. Registrar Novo Aluno")
        print("2. Fazer Check-in")
        print("3. Fazer Check-out")
        print("4. Listar Alunos Cadastrados")
        print("5. Ver Histórico de Registros")
        print("6. Sair")
        print("=" * 41)

        escolha = input("Digite sua opção: ")

        if escolha == '1':
            nome = input("Digite o nome completo do aluno: ")
            telefone = input("Digite o telefone do aluno: ")
            novo_id = gerenciador.registrar_aluno(nome, telefone)
            if novo_id:
                print(f"Guarde este ID! -> {novo_id}")
        elif escolha == '2':
            aluno_id = input("Digite o ID do aluno para Check-in: ")
            gerenciador.registrar_evento(aluno_id, 'check-in')
        elif escolha == '3':
            aluno_id = input("Digite o ID do aluno para Check-out: ")
            gerenciador.registrar_evento(aluno_id, 'check-out')
        elif escolha == '4':
            gerenciador.listar_alunos()
        elif escolha == '5':
            gerenciador.listar_registros()
        elif escolha == '6':
            print("\nSaindo do sistema. Até logo!")
            gerenciador.fechar_conexao()
            break
        else:
            print("\n❌ Opção inválida. Por favor, tente novamente.")