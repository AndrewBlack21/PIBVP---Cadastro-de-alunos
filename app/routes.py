# app/routes.py
from flask import render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import check_password_hash
from functools import wraps
import os

from app import app, DB_PATH
from app.database import GerenciadorAlunos

db = GerenciadorAlunos(db_path=DB_PATH)

# --- DECORADORES DE PERMISSÃO ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in') or session.get('role') != 'admin':
            abort(403) # Proibido
        return f(*args, **kwargs)
    return decorated_function

# --- ROTAS ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.buscar_usuario_por_nome(username)

        if user and check_password_hash(user['password_hash'], password):
            session['logged_in'] = True
            session['username'] = user['username']
            session['role'] = user['role'] # Salva o papel do usuário na sessão
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha incorretos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() # Limpa toda a sessão
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required # Qualquer usuário logado (admin ou professor) pode ver
def dashboard():
    registros = db.get_registros_do_dia()
    alunos = db.get_todos_os_alunos()
    return render_template('dashboard.html', registros=registros, alunos=alunos)

# --- Rotas do Administrador ---


# --- Rotas do Professor (e Admin) ---
@app.route('/registrar', methods=['GET', 'POST'])
@login_required # Qualquer usuário logado pode registrar alunos
def registrar_aluno():
    if request.method == 'POST':
        # ... (lógica de registrar aluno sem alteração) ...
        nome = request.form['nome']
        telefone = request.form['telefone']
        if not nome:
            flash('O campo nome é obrigatório.', 'danger')
            return redirect(url_for('registrar_aluno'))
        novo_id = db.registrar_aluno(nome, telefone)
        return redirect(url_for('registro_sucesso', novo_id=novo_id, nome_aluno=nome))
    return render_template('registrar_aluno.html')

@app.route('/registro_sucesso')
@login_required
def registro_sucesso():
    novo_id = request.args.get('novo_id')
    nome_aluno = request.args.get('nome_aluno')
    return render_template('registro_sucesso.html', novo_id=novo_id, nome_aluno=nome_aluno)

@app.route('/configurar-chave', methods=['GET', 'POST'])
@login_required
def configurar_chave():
    if request.method == 'POST':
        # ... (lógica de configurar chave sem alteração) ...
        nova_chave = request.form.get('chave')
        if db.definir_chave_registro(nova_chave):
            flash('Chave de inscrição atualizada com sucesso!', 'success')
        else:
            flash('Erro ao salvar a chave.', 'danger')
        return redirect(url_for('configurar_chave'))
    chave_atual = db.obter_chave_registro()
    return render_template('configurar_chave.html', chave_atual=chave_atual)

# --- Rotas Públicas (Aluno) ---
# ... (todas as rotas de /inscricao, /aluno, etc. continuam iguais e sem decoradores) ...
@app.route('/inscricao', methods=['GET', 'POST'])
def inscricao():
    if request.method == 'POST':
        nome = request.form.get('nome')
        telefone = request.form.get('telefone')
        chave_digitada = request.form.get('chave_inscricao')
        chave_correta = db.obter_chave_registro()
        if not chave_correta:
            flash('As inscrições não estão abertas no momento. Fale com seu professor.', 'warning')
            return redirect(url_for('inscricao'))
        if chave_digitada == chave_correta:
            novo_id = db.registrar_aluno(nome, telefone)
            flash(f'Inscrição realizada com sucesso, {nome}! Seu ID de acesso é {novo_id}. Guarde-o com segurança.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Chave de Inscrição incorreta. Tente novamente.', 'danger')
            return redirect(url_for('inscricao'))
    return render_template('inscricao.html')

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

@app.route('/painel-admin', methods=['GET', 'POST'])
@admin_required # Apenas administradores podem acessar
def painel_admin():
    # Lógica para o formulário de cadastro de professor
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Cria o usuário com o papel 'professor'
        success = db.criar_usuario(username, password, role='professor')
        if success:
            flash(f'Professor "{username}" cadastrado com sucesso!', 'success')
        else:
            flash(f'O nome de usuário "{username}" já existe.', 'danger')
        return redirect(url_for('painel_admin')) # Redireciona para a mesma página

    # Lógica para exibir os registros do dia
    registros = db.get_registros_do_dia()
    return render_template('painel_admin.html', registros=registros)

app.secret_key = os.environ.get('SECRET_KEY', 'uma-chave-padrao-para-desenvolvimento')