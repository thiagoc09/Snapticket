from flask import render_template, request, redirect, url_for, flash, current_app, session  # Adicionar session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import main
from .. import db
from ..models import Usuario, Evento
import os
from datetime import datetime

# Função auxiliar para validar o arquivo de upload
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def home():
    # Verifica se o usuário está logado
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('main.login'))
    eventos = Evento.query.all()
    return render_template('home.html', eventos=eventos)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha_hash, senha):
            session['logged_in'] = True  # Define a sessão como logada
            return redirect(url_for('main.home'))
        else:
            flash('E-mail ou senha incorretos')
            return render_template('login.html')

    # Certifica-se de limpar o estado da sessão ao carregar a página de login
    session.pop('logged_in', None)
    return render_template('login.html')

@main.route('/logout', methods=['POST'])
def logout():
    session.pop('logged_in', None)  # Limpa a sessão ao fazer logout
    return redirect(url_for('main.login'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        cpf = request.form.get('cpf')
        senha = request.form.get('senha')
        
        # Verifica se a senha foi fornecida
        if not senha:
            flash('Senha é obrigatória.')
            return redirect(url_for('main.register'))
        
        # Verifica se o email já está cadastrado
        if Usuario.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.')
            return redirect(url_for('main.register'))
        
        selfie = request.files.get('selfie')
        selfie_path = None
        if selfie and allowed_file(selfie.filename):
            filename = secure_filename(selfie.filename)
            selfie_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            selfie.save(selfie_path)
        else:
            flash('Tipo de arquivo não permitido para selfie.')
            return redirect(url_for('main.register'))
        
        # Criar novo usuário e salvar no banco de dados
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            telefone=telefone,
            cpf=cpf,
            senha_hash=generate_password_hash(senha),  # Usando hash novamente
            caminho_selfie=selfie_path
        )
        
        db.session.add(novo_usuario)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Erro ao registrar usuário. Por favor, tente novamente.')
            return redirect(url_for('main.register'))
        
        return redirect(url_for('main.login'))
    
    # Este return será executado se o método for GET
    return render_template('register.html')

@main.route('/cadastro_evento', methods=['GET', 'POST'])
def cadastro_evento():
    if request.method == 'POST':
        nome_evento = request.form.get('nome_evento')
        data_evento_str = request.form.get('data_evento')
        localizacao = request.form.get('localizacao')
        descricao = request.form.get('descricao')
        
        try:
            data_evento = datetime.strptime(data_evento_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Formato de data inválido.')
            return redirect(url_for('main.cadastro_evento'))

        foto_capa = request.files.get('foto_capa')
        if foto_capa and allowed_file(foto_capa.filename):
            filename_capa = secure_filename(foto_capa.filename)
            foto_capa_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename_capa)
            foto_capa.save(foto_capa_path)
        else:
            foto_capa_path = None
        
        novo_evento = Evento(
            nome_evento=nome_evento,
            data_evento=data_evento,
            localizacao=localizacao,
            descricao=descricao,
            foto_capa=foto_capa_path
        )
        db.session.add(novo_evento)
        db.session.commit()

        return redirect(url_for('main.home'))

    return render_template('cadastro_evento.html')
