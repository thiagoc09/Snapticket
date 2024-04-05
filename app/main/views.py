# app/main/views.py
from flask import render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from . import main  # Importação do Blueprint 'main'
from .. import db
from ..models import Usuario
import os

# Função auxiliar para validar o arquivo de upload
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rota para a página inicial que redireciona para a página de login
@main.route('/')
def home():
    return redirect(url_for('main.login'))

# Rota para a página de login
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # CREDENCIAIS DE LOGIN
        pass
    return render_template('login.html')

# Rota para a página de registro de usuário
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        cpf = request.form.get('cpf')
        senha = request.form.get('senha')
        
         # Verifique se a senha não está vazia
        if not senha:
            flash('Senha é obrigatória.')
            return redirect(url_for('main.register'))
        
        
        selfie = request.files.get('selfie')
        if selfie and allowed_file(selfie.filename):
            filename = secure_filename(selfie.filename)
            selfie_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            selfie.save(selfie_path)
        else:
            # Se não for um POST, simplesmente renderiza o template de registro
            flash('Tipo de arquivo não permitido.')
            return redirect(request.url)
        
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            telefone=telefone,
            cpf=cpf,
            caminho_selfie=selfie_path
        )
        novo_usuario.set_password(senha)
       
        db.session.add(novo_usuario)
        db.session.commit()
        
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/cadastro_evento', methods=['GET', 'POST'])
def cadastro_evento():
    if request.method == 'POST':
        nome_evento = request.form.get('nome_evento')
        data_evento = request.form.get('data_evento')
        localizacao = request.form.get('localizacao')
        descricao = request.form.get('descricao')

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