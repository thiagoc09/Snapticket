from flask import render_template, request, redirect, url_for, flash, current_app, session, jsonify  
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import main
from .. import db
from ..models import Usuario, Evento, ImagemEvento
import os

from datetime import datetime
from flask_login import login_user, logout_user, login_required, LoginManager, current_user

from app.face_recognition import compare_faces, load_image_bytes  # Importando as funções corretamente
from PIL import Image

# Configuração do LoginManager
login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Função auxiliar para validar o arquivo de upload
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def add_image_watermark(input_image_path, watermark_image_path, output_image_path, position=(0, 0), opacity=128):
    base_image = Image.open(input_image_path).convert("RGBA")
    watermark = Image.open(watermark_image_path).convert("RGBA")

    # Ajustar o tamanho da marca d'água
    ratio = min(base_image.size[0] / 4 / watermark.size[0], base_image.size[1] / 4 / watermark.size[1])
    new_size = (int(watermark.size[0] * ratio), int(watermark.size[1] * ratio))
    watermark = watermark.resize(new_size, Image.LANCZOS)  # Use LANCZOS instead of ANTIALIAS

    # Ajustar a opacidade da marca d'água
    watermark.putalpha(opacity)

    # Criar uma nova imagem para a marca d'água repetida
    transparent = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
    for y in range(0, base_image.size[1], watermark.size[1]):
        for x in range(0, base_image.size[0], watermark.size[0]):
            transparent.paste(watermark, (x, y), watermark)

    # Combinar a imagem base com a marca d'água repetida
    watermarked_image = Image.alpha_composite(base_image, transparent)

    # Converter para RGB e salvar
    watermarked_image = watermarked_image.convert("RGB")
    watermarked_image.save(output_image_path, "JPEG")

@main.route('/')
@login_required
def home():
    show_modal = request.args.get('show_modal')
    event_name = request.args.get('event_name')

    if event_name:
        eventos = Evento.query.filter(Evento.nome_evento.ilike(f"%{event_name}%")).all()
    else:
        eventos = Evento.query.all()
        
    return render_template('home.html', eventos=eventos, show_modal=show_modal)

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
        if foto_capa:
            foto_capa_filename = secure_filename(foto_capa.filename)
            foto_capa_path_fs = os.path.join(current_app.config['UPLOAD_FOLDER'], 'event_covers', foto_capa_filename)
            os.makedirs(os.path.dirname(foto_capa_path_fs), exist_ok=True)
            foto_capa.save(foto_capa_path_fs)
            foto_capa_path_db = os.path.join('uploads', 'event_covers', foto_capa_filename).replace('\\', '/')
            novo_evento.foto_capa = foto_capa_path_db

        # Quando salvar as fotos do evento
        fotos_evento = request.files.getlist('fotos_evento')
        for foto in fotos_evento:
            if foto:
                filename = secure_filename(foto.filename)
                evento_folder_rel_path = os.path.join('uploads', 'event_images', str(novo_evento.id))
                evento_folder_full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'event_images', str(novo_evento.id))
                if not os.path.exists(evento_folder_full_path):
                    os.makedirs(evento_folder_full_path)
                foto.save(os.path.join(evento_folder_full_path, filename))
                imagem_evento = ImagemEvento(evento_id=novo_evento.id, caminho_imagem=os.path.join(evento_folder_rel_path, filename))
                db.session.add(imagem_evento)

        db.session.commit()
        flash('Evento cadastrado com sucesso!')
        return redirect(url_for('main.home'))
    return render_template('cadastro_evento.html')

from flask import session

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
    
    # Inicializa o conjunto de fotos processadas na sessão se não existir
    if 'processed_photos' not in session:
        session['processed_photos'] = set()
    
    processed_photos = set(session['processed_photos'])

    for photo_name in os.listdir(event_photos_directory):
        if photo_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            photo_path = os.path.join(event_photos_directory, photo_name)
            if photo_path not in processed_photos and compare_faces(user_selfie_data, load_image_bytes(photo_path)):
                # Adiciona marca d'água e salva a imagem
                watermarked_path = os.path.join('uploads/event_images', str(event_id), f'wm_{photo_name}')
                os.makedirs(os.path.dirname(os.path.join('app/static', watermarked_path)), exist_ok=True)
                add_image_watermark(photo_path, 'app/static/images/logo.png', os.path.join('app/static', watermarked_path), position=(10, 10), opacity=150)
                matches.append(watermarked_path.replace('\\', '/'))
                processed_photos.add(photo_path)  # Marca a foto como processada

    # Atualiza a sessão com as fotos processadas
    session['processed_photos'] = list(processed_photos)

    if not matches:
        return redirect(url_for('main.home', show_modal='true'))
    else:
        return render_template('photos.html', photos=matches, event_id=event_id)

@main.route('/my_photos')
@login_required
def my_photos():
    # Lógica para buscar as fotos salvas pelo usuário
    return render_template('my_photos.html')

@main.route('/search_events', methods=['GET'])
@login_required
def search_events():
    event_name = request.args.get('event_name')
    eventos = Evento.query.filter(Evento.nome_evento.ilike(f"%{event_name}%")).all()
    results = [{
        "id": evento.id,
        "nome_evento": evento.nome_evento,
        "data_evento": evento.data_evento.strftime('%Y-%m-%d'),
        "foto_capa": url_for('static', filename=evento.foto_capa)
    } for evento in eventos]
    return jsonify(results)