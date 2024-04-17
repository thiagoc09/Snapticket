from flask import render_template, request, redirect, url_for, flash, current_app, session  # Adicionar session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import main
from .. import db
from ..models import Usuario, Evento
import os
from datetime import datetime
from flask_login import login_user, logout_user, login_required, LoginManager

login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

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
    for evento in eventos:
        if not evento.foto_capa:
            evento.foto_capa = current_app.config['DEFAULT_EVENT_COVER']  # Caminho da imagem padrão
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

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi deslogado com sucesso.')
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

        selfie_path = None
       
           # Código para registro de usuário
        selfie = request.files.get('selfie')
        if selfie and allowed_file(selfie.filename):
            filename = secure_filename(selfie.filename)
            selfie_path = os.path.join(current_app.config['USER_SELFIES_FOLDER'], filename)
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

        # Tenta converter a string da data em um objeto datetime
        try:
            data_evento = datetime.strptime(data_evento_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Formato de data inválido.')
            return redirect(url_for('main.cadastro_evento'))

        # Lida com o upload da foto de capa
        foto_capa = request.files.get('foto_capa')
        if foto_capa and allowed_file(foto_capa.filename):
            filename_capa = secure_filename(foto_capa.filename)
            foto_capa_path = os.path.join(current_app.config['EVENT_COVERS_FOLDER'], filename_capa)
            foto_capa.save(foto_capa_path)
            foto_capa_path = 'images/eventos/' + filename_capa  # Caminho relativo para uso no HTML
        else:
            foto_capa_path = 'images/eventos/default_cover.jpg'  # Caminho padrão para imagem de capa

        # Cria novo evento com as informações recebidas e o caminho da foto de capa
        novo_evento = Evento(
            nome_evento=nome_evento,
            data_evento=data_evento,
            localizacao=localizacao,
            descricao=descricao,
            foto_capa=foto_capa_path
        )
        
        # Adiciona o novo evento ao banco de dados e commita as alterações
        db.session.add(novo_evento)
        db.session.commit()

        # Redireciona para a home após o sucesso no cadastro
        return redirect(url_for('main.home'))

    # Retorna a página de cadastro de evento caso seja um GET ou ocorra algum erro
    return render_template('cadastro_evento.html')
