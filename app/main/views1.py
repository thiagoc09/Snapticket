from flask import render_template, request, redirect, url_for, flash, current_app, session  # Adicionar session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import main
from .. import db
from ..models import Usuario, Evento, ImagemEvento
import os
from datetime import datetime
from flask_login import login_user, logout_user, login_required, LoginManager, current_user
from app.face_recognition import compare_faces, load_image_bytes  # Importando as funções corretamente



login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Função auxiliar para validar o arquivo de upload
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route('/')
@login_required  # Garante que esta rota requer um usuário logado
def home():
    show_modal = request.args.get('show_modal', 'false') == 'true'
    eventos = Evento.query.all()
    for evento in eventos:
        if not evento.foto_capa:
            evento.foto_capa = current_app.config['DEFAULT_EVENT_COVER']
    return render_template('home.html', eventos=eventos, show_modal=show_modal)



# @main.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         senha = request.form.get('senha')

#         usuario = Usuario.query.filter_by(email=email).first()

#         if usuario and check_password_hash(usuario.senha_hash, senha):
#             session['logged_in'] = True  # Define a sessão como logada
#             return redirect(url_for('main.home'))
#         else:
#             flash('E-mail ou senha incorretos')
#             return render_template('login.html')

#     # Certifica-se de limpar o estado da sessão ao carregar a página de login
#     session.pop('logged_in', None)
#     return render_template('login.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha_hash, senha):
            login_user(usuario)  # Registra o usuário na sessão usando Flask-Login
            return redirect(url_for('main.home'))
        else:
            flash('E-mail ou senha incorretos')
            return render_template('login.html')

    return render_template('login.html')



@main.route('/logout', methods=['GET','POST'])
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
        
        if not senha:
            flash('Senha é obrigatória.')
            return redirect(url_for('main.register'))
        
        if Usuario.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.')
            return redirect(url_for('main.register'))

        # Criar novo usuário e tentar salvar no banco de dados
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            telefone=telefone,
            cpf=cpf,
            senha_hash=generate_password_hash(senha)  # Usando hash da senha
        )
        db.session.add(novo_usuario)
        
        try:
            db.session.commit()  # Salvar usuário para garantir que temos um user_id
        except Exception as e:
            db.session.rollback()
            flash('Erro ao registrar usuário. Por favor, tente novamente.')
            return redirect(url_for('main.register'))

        # Processar o upload da selfie após o usuário ser salvo
        selfie = request.files.get('selfie')
        if selfie and allowed_file(selfie.filename):
            filename = secure_filename(f'{novo_usuario.id}.jpg')  # Nome do arquivo como ID do usuário
            selfie_path = os.path.join(current_app.config['USER_SELFIES_FOLDER'], filename)
            selfie.save(selfie_path)
            novo_usuario.caminho_selfie = selfie_path  # Atualizar o caminho da selfie no banco de dados
            db.session.commit()
        else:
            flash('Tipo de arquivo não permitido para selfie.')
            return redirect(url_for('main.register'))
        
        return redirect(url_for('main.login'))
    
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
        # No local onde você obtém o arquivo da foto de capa
        if foto_capa:
            foto_capa_filename = secure_filename(foto_capa.filename)
            # Construa o caminho onde a imagem será salva
            foto_capa_path_fs = os.path.join(current_app.config['UPLOAD_FOLDER'], 'event_covers', foto_capa_filename)
            # Garanta que o diretório onde a imagem será salva existe
            os.makedirs(os.path.dirname(foto_capa_path_fs), exist_ok=True)
            # Salve a imagem
            foto_capa.save(foto_capa_path_fs)
            # Construa o caminho relativo para salvar no banco de dados
            foto_capa_path_db = os.path.join('uploads', 'event_covers', foto_capa_filename)
            print(foto_capa_path_db)
            foto_capa_path_db_1 = foto_capa_path_db.replace('\\', '/')

            # Salve o caminho relativo no banco de dados
            novo_evento.foto_capa = foto_capa_path_db_1
            
        # Quando salvar as fotos do evento
        fotos_evento = request.files.getlist('fotos_evento')
        for foto in fotos_evento:
            if foto:
                filename = secure_filename(foto.filename)
                # Cria o caminho relativo onde a imagem será salva
                evento_folder_rel_path = os.path.join('uploads', 'event_images', str(novo_evento.id))
                evento_folder_full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'event_images', str(novo_evento.id))
                if not os.path.exists(evento_folder_full_path):
                    os.makedirs(evento_folder_full_path)
                foto.save(os.path.join(evento_folder_full_path, filename))
                # Salva apenas o caminho relativo no banco de dados
                imagem_evento = ImagemEvento(evento_id=novo_evento.id, caminho_imagem=os.path.join(evento_folder_rel_path, filename))
                db.session.add(imagem_evento)




        db.session.commit()
        flash('Evento cadastrado com sucesso!')
        return redirect(url_for('main.home'))
    return render_template('cadastro_evento.html')
    
# view_photos
@main.route('/view_photos/<int:event_id>')
@login_required
def view_photos(event_id):
    user_id = current_user.id
    user_selfie_path = f'app/static/uploads/user_selfies/{user_id}.jpg'
    event_photos_directory = f'app/static/uploads/event_images/{event_id}'

    if not os.path.exists(user_selfie_path):
        flash('Selfie do usuário não encontrada.', 'error')
        return redirect(url_for('main.home'))

    user_selfie_data = load_image_bytes(user_selfie_path)
    matches = []

    for photo_name in os.listdir(event_photos_directory):
        if photo_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            photo_path = os.path.join(f'event_images/{event_id}', photo_name)  # Ajuste aqui para evitar duplicação de caminhos
            if compare_faces(user_selfie_data, load_image_bytes(os.path.join(event_photos_directory, photo_name))):
                matches.append(os.path.join('uploads/event_images', str(event_id), photo_name).replace('\\', '/'))

    if not matches:
        return redirect(url_for('main.home', show_modal='true'))
    else:
        return render_template('photos.html', photos=matches, event_id=event_id)
