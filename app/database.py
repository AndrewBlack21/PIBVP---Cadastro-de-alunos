# app/database.py
import sqlite3
from datetime import datetime
import os
from werkzeug.security import generate_password_hash # Importa a função para criptografar a senha

class GerenciadorAlunos:
    def __init__(self, db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.criar_tabelas()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def criar_tabelas(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS alunos (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                telefone TEXT
            )""")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id TEXT NOT NULL,
                tipo TEXT NOT NULL,
                horario TEXT NOT NULL,
                FOREIGN KEY (aluno_id) REFERENCES alunos (id)
            )""")
            # NOVA TABELA PARA USUÁRIOS DA INSTITUIÇÃO (PROFESSORES)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )""")
            conn.commit()

    # --- Funções de Usuário ---
    def criar_usuario(self, username, password):
        """Cria um novo usuário com senha criptografada."""
        password_hash = generate_password_hash(password)
        with self._get_conn() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO usuarios (username, password_hash) VALUES (?, ?)", (username, password_hash))
                conn.commit()
                return True
            except sqlite3.IntegrityError: # Ocorre se o username já existir
                return False

    def buscar_usuario_por_nome(self, username):
        """Busca um usuário pelo seu nome de usuário."""
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
            return cursor.fetchone()

    # --- Funções de Aluno (sem alterações) ---
    def registrar_aluno(self, nome, telefone):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO alunos (nome, telefone) VALUES (?, ?)", (nome, telefone))
            id_numerico = cursor.lastrowid 
            id_formatado = "{:04d}".format(id_numerico)
            cursor.execute("UPDATE alunos SET id = ? WHERE ROWID = ?", (id_formatado, id_numerico))
            conn.commit()
            return id_formatado

    def registrar_evento(self, aluno_id, tipo):
        horario_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO registros (aluno_id, tipo, horario) VALUES (?, ?, ?)", (aluno_id, tipo, horario_atual))
            conn.commit()

    def buscar_aluno_por_id(self, aluno_id):
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM alunos WHERE id = ?", (aluno_id,))
            return cursor.fetchone()

    def get_ultimo_registro(self, aluno_id):
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM registros WHERE aluno_id = ? ORDER BY horario DESC LIMIT 1", (aluno_id,))
            return cursor.fetchone()
    
    def get_registros_do_dia(self):
        hoje = datetime.now().strftime('%Y-%m-%d')
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query = """
            SELECT r.horario, r.tipo, a.nome
            FROM registros r JOIN alunos a ON r.aluno_id = a.id
            WHERE DATE(r.horario) = ?
            ORDER BY r.horario DESC
            """
            cursor.execute(query, (hoje,))
            return cursor.fetchall()

    def get_todos_os_alunos(self):
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM alunos WHERE id IS NOT NULL ORDER BY nome")
            return cursor.fetchall()
        
    def verificar_se_existem_usuarios(self):
        """Verifica se há pelo menos um usuário na tabela de usuarios. Retorna True ou False."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(id) FROM usuarios")
            count = cursor.fetchone()[0]
            return count > 0