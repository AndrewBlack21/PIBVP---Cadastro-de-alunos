# app/routes.py
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from app import app, DB_PATH
from app.database import GerenciadorAlunos
import os

db = GerenciadorAlunos(db_path=DB_PATH)

@app.route('/')
def index():
    return render_template('index.html')

# --- Rotas da Instituição ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Se não houver usuários, redireciona para a página de criação do primeiro admin
    if not db.verificar_se_existem_usuarios():
        flash('Nenhum administrador encontrado. Por favor, crie a primeira conta.', 'info')
        return redirect(url_for('criar_primeiro_usuario'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.buscar_usuario_por_nome(username)

        if user and check_password_hash(user['password_hash'], password):
            session['logged_in'] = True
            session['username'] = user['username']
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha incorretos. Tente novamente.', 'danger')
            
    return render_template('login.html')

@app.route('/criar-primeiro-usuario', methods=['GET', 'POST'])
def criar_primeiro_usuario():
    # Se já existir um usuário, esta página não pode ser acessada
    if db.verificar_se_existem_usuarios():
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password_confirm']

        if password != password_confirm:
            flash('As senhas não coincidem.', 'danger')
            return redirect(url_for('criar_primeiro_usuario'))
        
        success = db.criar_usuario(username, password)
        if success:
            flash(f'Usuário administrador "{username}" criado com sucesso! Agora você pode fazer o login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(f'O nome de usuário "{username}" já foi pego (isso não deveria acontecer na primeira vez).', 'danger')

    return render_template('criar_primeiro_usuario.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    registros = db.get_registros_do_dia()
    alunos = db.get_todos_os_alunos()
    return render_template('dashboard.html', registros=registros, alunos=alunos)

# ... (O resto do arquivo, com as rotas de registrar_aluno, registro_sucesso e a área do aluno, continua exatamente igual) ...
@app.route('/registrar', methods=['GET', 'POST'])
def registrar_aluno():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        if not nome:
            flash('O campo nome é obrigatório.', 'danger')
            return redirect(url_for('registrar_aluno'))
        novo_id = db.registrar_aluno(nome, telefone)
        return redirect(url_for('registro_sucesso', novo_id=novo_id, nome_aluno=nome))
    return render_template('registrar_aluno.html')

@app.route('/registro_sucesso')
def registro_sucesso():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    novo_id = request.args.get('novo_id')
    nome_aluno = request.args.get('nome_aluno')
    return render_template('registro_sucesso.html', novo_id=novo_id, nome_aluno=nome_aluno)

@app.route('/aluno', methods=['GET', 'POST'])
def acesso_aluno():
    if request.method == 'POST':
        aluno_id = request.form['aluno_id']
        aluno = db.buscar_aluno_por_id(aluno_id)
        if aluno:
            return redirect(url_for('status_aluno', aluno_id=aluno_id))
        else:
            flash('ID de aluno não encontrado. Tente novamente.', 'warning')
            return redirect(url_for('acesso_aluno'))
    return render_template('acesso_aluno.html')

@app.route('/aluno/<aluno_id>')
def status_aluno(aluno_id):
    aluno = db.buscar_aluno_por_id(aluno_id)
    if not aluno:
        return redirect(url_for('acesso_aluno'))
    ultimo_registro = db.get_ultimo_registro(aluno_id)
    status_atual = ultimo_registro['tipo'] if ultimo_registro else 'check-out'
    return render_template('status_aluno.html', aluno=aluno, status_atual=status_atual)

@app.route('/aluno/<aluno_id>/registrar_evento', methods=['POST'])
def registrar_evento_web(aluno_id):
    tipo_evento = request.form['tipo_evento']
    db.registrar_evento(aluno_id, tipo_evento)
    acao = "Check-in" if tipo_evento == "check-in" else "Check-out"
    flash(f'{acao} realizado com sucesso!', 'info')
    return redirect(url_for('status_aluno', aluno_id=aluno_id))

app.secret_key = os.environ.get('SECRET_KEY', 'uma-chave-padrao-para-desenvolvimento')