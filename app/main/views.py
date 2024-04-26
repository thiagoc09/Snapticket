from flask import render_template, request, redirect, url_for, flash, current_app, session  # Adicionar session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import main
from .. import db
from ..models import Usuario, Evento, ImagemEvento
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

@main.route('/logout', methods=['GET', 'POST'])
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
        nome_evento = request.form['nome_evento']
        data_evento_str = request.form['data_evento']
        localizacao = request.form['localizacao']
        descricao = request.form['descricao']

        # Convertendo a string de data para um objeto date
        try:
            data_evento = datetime.strptime(data_evento_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Formato de data inválido.')
            return redirect(url_for('cadastro_evento'))

        # Instanciando um novo objeto Evento
        novo_evento = Evento(
            nome_evento=nome_evento,
            data_evento=data_evento,
            localizacao=localizacao,
            descricao=descricao
        )
        db.session.add(novo_evento)
        db.session.commit()  # Commit para obter o ID do evento

        # Salvando a foto de capa
        foto_capa = request.files.get('foto_capa')

        if foto_capa:
            foto_capa_filename = secure_filename(foto_capa.filename)
            foto_capa_path = os.path.join(current_app.config['EVENT_COVERS_FOLDER'], foto_capa_filename)
            foto_capa.save(os.path.join('app', 'static', foto_capa_path))
            novo_evento.foto_capa = foto_capa_path  # Salva apenas o caminho relativo


        # Salvando as fotos do evento
        fotos_evento = request.files.getlist('fotos_evento')
        for foto in fotos_evento:
            if foto:
                filename = secure_filename(foto.filename)
                evento_folder = os.path.join(current_app.config['EVENT_IMAGES_FOLDER'], str(novo_evento.id))
                if not os.path.exists(evento_folder):
                    os.makedirs(evento_folder)
                path = os.path.join(evento_folder, filename)
                foto.save(path)
                # Adicionando a foto do evento ao banco de dados (ajuste o nome do modelo conforme o seu)
                imagem_evento = ImagemEvento(evento_id=novo_evento.id, caminho_imagem=path)
                db.session.add(imagem_evento)

        db.session.commit()
        flash('Evento cadastrado com sucesso!')
        return redirect(url_for('main.home'))
    return render_template('cadastro_evento.html')