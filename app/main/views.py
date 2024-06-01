import logging
import time
from flask import render_template, request, redirect, url_for, flash, current_app, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import main
from .. import db
from ..models import Usuario, Evento, ImagemEvento, FotosGaleria
import os
from datetime import datetime
from flask_login import login_user, logout_user, login_required, LoginManager, current_user
from app.face_recognition import load_image_bytes  # Não precisamos mais do compare_faces
from PIL import Image
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Configuração do LoginManager
login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Configurar cliente do Rekognition
rekognition_client = boto3.client('rekognition', region_name='us-west-2')  # Ajuste a região conforme necessário

# Função auxiliar para validar o arquivo de upload
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def add_image_watermark(input_image_path, watermark_image_path, output_image_path, position=(0, 0), opacity=128):
#     if not os.path.exists(output_image_path):
#         base_image = Image.open(input_image_path).convert("RGBA")
#         watermark = Image.open(watermark_image_path).convert("RGBA")

#         ratio = min(base_image.size[0] / 4 / watermark.size[0], base_image.size[1] / 4 / watermark.size[1])
#         new_size = (int(watermark.size[0] * ratio), int(watermark.size[1] * ratio))
#         watermark = watermark.resize(new_size, Image.LANCZOS)

#         watermark.putalpha(opacity)

#         transparent = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
#         for y in range(0, base_image.size[1], watermark.size[1]):
#             for x in range(0, base_image.size[0], watermark.size[0]):
#                 transparent.paste(watermark, (x, y), watermark)

#         watermarked_image = Image.alpha_composite(base_image, transparent)
#         watermarked_image = watermarked_image.convert("RGB")
#         watermarked_image.save(output_image_path, "JPEG")

def compare_faces_aws(source_image_bytes, target_image_bytes):
    try:
        response = rekognition_client.compare_faces(
            SourceImage={'Bytes': source_image_bytes},
            TargetImage={'Bytes': target_image_bytes},
            SimilarityThreshold=90  # Ajuste o limiar conforme necessário
        )
        return len(response['FaceMatches']) > 0
    except (NoCredentialsError, PartialCredentialsError) as e:
        logging.error(f"Erro de credenciais AWS: {e}")
        return False
    except Exception as e:
        logging.error(f"Erro ao comparar faces com AWS Rekognition: {e}")
        return False

@main.route('/')
def home():
    start_time = time.time()
    event_name = request.args.get('event_name')
    if event_name:
        eventos = Evento.query.filter(Evento.nome_evento.ilike(f'%{event_name}%')).all()
    else:
        eventos = Evento.query.all()

    show_modal = request.args.get('show_modal', False)
    elapsed_time = time.time() - start_time
    logging.info(f"Home page loaded in {elapsed_time:.2f} seconds")

    # Passando 'logged_in' para o template para usar na renderização condicional do header e na interatividade dos eventos
    return render_template('home.html', eventos=eventos, show_modal=show_modal, logged_in=current_user.is_authenticated)
    
    
# @main.route('/')
# def home():
#     return render_template('home.html')
# Configuração do logger
logger = logging.getLogger(__name__)
# Configura o nível de log para info para capturar informações detalhadas durante o processo de login
logging.basicConfig(level=logging.INFO)

@main.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            logger.info(f'Tentativa de login com email: {email}')

            user = Usuario.query.filter_by(email=email).first()
            if user:
                logger.info(f'Usuário encontrado: {user.nome}')
                if check_password_hash(user.senha_hash, password):
                    login_user(user)
                    logger.info('Login bem-sucedido')
                    return redirect(url_for('main.home'))
                else:
                    logger.info('Senha incorreta')
            else:
                logger.info('Usuário não encontrado')

            flash('Login falhou. Verifique suas credenciais.')
        return render_template('login.html')
    except Exception as e:
        logger.error(f'Erro durante o login: {e}')
        flash('Um erro ocorreu durante o login.')
        return render_template('login.html'), 500

@main.route('/logout')
@login_required
def logout():
    user_id = current_user.id
    session.pop(f'user_{user_id}_photos', None)
    session.pop(f'user_{user_id}_processed_photos', None)
    logout_user()
    flash('Você foi deslogado com sucesso.', 'success')
    return redirect(url_for('main.home'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirm_senha')

        if senha != confirmar_senha:
            flash('Senhas não coincidem.')
            return redirect(url_for('main.register'))

        if not senha:
            flash('Senha é obrigatória.')
            return redirect(url_for('main.register'))

        if Usuario.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.')
            return redirect(url_for('main.register'))

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=generate_password_hash(senha)
        )
        db.session.add(novo_usuario)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Erro ao registrar usuário. Por favor, tente novamente.')
            return redirect(url_for('main.register'))

        selfie = request.files.get('selfie')
        if selfie and allowed_file(selfie.filename):
            filename = secure_filename(f'{novo_usuario.id}.jpg')
            selfie_path = os.path.join(current_app.config['USER_SELFIES_FOLDER'], filename)
            selfie.save(selfie_path)
            novo_usuario.caminho_selfie = selfie_path
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash('Erro ao salvar a selfie.')
                return redirect(url_for('main.register'))
        else:
            flash('Tipo de arquivo não permitido para selfie.')
            return redirect(url_for('main.register'))

        flash('Cadastro realizado com sucesso!')
        return redirect(url_for('main.login'))
    return render_template('register.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}
@main.route('/cadastro_evento', methods=['GET', 'POST'])

def cadastro_evento():
    if request.method == 'POST':
        nome_evento = request.form.get('nome_evento')
        data_evento = request.form.get('data_evento')
        plano_tipo = request.form.get('plano_tipo')

        try:
            data_evento = datetime.strptime(data_evento, '%Y-%m-%d').date()
        except ValueError:
            flash('Formato de data inválido.')
            return redirect(url_for('cadastro_evento'))

        novo_evento = Evento(
            nome_evento=nome_evento,
            data_evento=data_evento,
            plano_tipo=plano_tipo
        )
        db.session.add(novo_evento)
        db.session.commit()  # Commit aqui para gerar o ID do evento

        # Processando a foto de capa
        foto_capa = request.files.get('foto_capa')
        if foto_capa and foto_capa.filename != '':
            foto_capa_filename = secure_filename(foto_capa.filename)
            foto_capa_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'event_covers', foto_capa_filename)
            foto_capa.save(foto_capa_path)
            novo_evento.foto_capa = os.path.join('uploads', 'event_covers', foto_capa_filename).replace('\\', '/')

        # Processando múltiplas fotos do evento
        fotos_evento = request.files.getlist('fotos_evento')
        for foto in fotos_evento:
            if foto and foto.filename != '':
                filename = secure_filename(foto.filename)
                evento_folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'event_photos', str(novo_evento.id))
                os.makedirs(evento_folder_path, exist_ok=True)
                foto_path = os.path.join(evento_folder_path, filename)
                foto.save(foto_path)
                imagem_evento = ImagemEvento(
                    evento_id=novo_evento.id,
                    caminho_imagem=os.path.join('uploads', 'event_photos', str(novo_evento.id), filename)
                )
                db.session.add(imagem_evento)

        db.session.commit()  # Final commit para salvar tudo
        flash('Evento cadastrado com sucesso!')
        return redirect(url_for('main.home'))

    return render_template('cadastro_evento.html')

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

@main.route('/my_photos')
@login_required
def my_photos():
    user_id = current_user.id
    user_photos = session.get(f'user_{user_id}_photos', [])
    return render_template('my_photos.html', photos=user_photos)

@main.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    photo_path = request.form.get('photo_path')
    if photo_path:
        user_id = current_user.id
        cart_photos = session.get(f'user_{user_id}_cart', [])
        if photo_path not in cart_photos:
            cart_photos.append(photo_path)
            session[f'user_{user_id}_cart'] = cart_photos
            flash('Foto adicionada ao carrinho com sucesso.')
        else:
            flash('Esta foto já está no carrinho.')
    return redirect(url_for('main.view_photos', event_id=request.form.get('event_id')))

@main.route('/cart')
@login_required
def cart():
    user_id = current_user.id
    cart_photos = session.get(f'user_{user_id}_cart', [])
    return render_template('cart.html', photos=cart_photos)

from flask import redirect, url_for, render_template, session
from flask_login import login_required, current_user
import os
import time
from werkzeug.utils import secure_filename


def add_image_watermark(input_image_path, watermark_image_path, output_image_path, position=(0, 0), opacity=128):
    base_image = Image.open(input_image_path).convert("RGBA")
    watermark = Image.open(watermark_image_path).convert("RGBA")

    ratio = min(base_image.size[0] / 4 / watermark.size[0], base_image.size[1] / 4 / watermark.size[1])
    new_size = (int(watermark.size[0] * ratio), int(watermark.size[1] * ratio))
    watermark = watermark.resize(new_size, Image.LANCZOS)

    watermark.putalpha(opacity)

    transparent = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
    for y in range(0, base_image.size[1], watermark.size[1]):
        for x in range(0, base_image.size[0], watermark.size[0]):
            transparent.paste(watermark, (x, y), watermark)

    watermarked_image = Image.alpha_composite(base_image, transparent)
    watermarked_image = watermarked_image.convert("RGB")
    
    # Garantindo que o diretório de saída exista
    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    
    watermarked_image.save(output_image_path, "JPEG")

@main.route('/view_photos/<int:event_id>')
@login_required
def view_photos(event_id):
    start_time = time.time()
    user_id = current_user.id
    user_selfie_path = f'app/static/uploads/user_selfies/{user_id}.jpg'
    event_photos_directory = f'app/static/uploads/event_photos/{event_id}'
    logo_path = 'app/static/images/logo.png'

    evento = Evento.query.get(event_id)
    if not evento:
        flash('Evento não encontrado.', 'error')
        return redirect(url_for('main.home'))

    if not os.path.exists(user_selfie_path):
        flash('Selfie do usuário não encontrada.', 'error')
        return redirect(url_for('main.home'))

    plano_tipo = evento.plano_tipo
    user_selfie_data = load_image_bytes(user_selfie_path)
    matches = session.get(f'user_{user_id}_photos', {})
    processed_photos = session.get(f'user_{user_id}_processed_photos', [])

    photos_found = False
    for photo_name in os.listdir(event_photos_directory):
        if photo_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            photos_found = True
            photo_path = os.path.join(event_photos_directory, photo_name)
            photo_relative_path = os.path.join(f'uploads/event_photos/{event_id}', photo_name).replace('\\', '/')

            if photo_relative_path not in processed_photos:
                if compare_faces_aws(user_selfie_data, load_image_bytes(photo_path)):
                    if plano_tipo == 'monetize':
                        watermark_output_path = os.path.join('app/static/uploads/watermarked_photos', f'watermarked_{photo_name}')
                        add_image_watermark(photo_path, logo_path, watermark_output_path)
                        matches[photo_relative_path] = watermark_output_path.replace('app/static/', '').replace('\\', '/')
                    else:
                        matches[photo_relative_path] = photo_relative_path
                    processed_photos.append(photo_relative_path)

    session[f'user_{user_id}_photos'] = matches
    session[f'user_{user_id}_processed_photos'] = processed_photos
    end_time = time.time()
    logging.info(f"Processed event {event_id} for user {user_id} in {end_time - start_time:.2f} seconds")

    nome = current_user.nome
    quantidade_fotos = len(matches)
    nome_evento = evento.nome_evento
    if quantidade_fotos == 1:
        mensagem_quantidade_fotos = "foi encontrado 1 momento seu"
    else:
        mensagem_quantidade_fotos = f"foram encontrados {quantidade_fotos} momentos seus"

    return render_template('photos.html', 
                           fotos=list(matches.values()), 
                           event_id=event_id, 
                           fotos_encontradas=photos_found,
                           nome=nome,
                           mensagem_quantidade_fotos=mensagem_quantidade_fotos,
                           nome_evento=nome_evento,
                           plano_tipo=plano_tipo)

@main.route('/galeria')
@login_required
def galeria():
    fotos = FotosGaleria.query.filter_by(user_id=current_user.id).all()
    return render_template('galeria.html', fotos=fotos)

@main.route('/save_to_gallery', methods=['POST'])
@login_required
def save_to_gallery():
    data = request.get_json()
    foto_path = data.get('foto')
    
    if foto_path:
        nova_foto = FotosGaleria(
            user_id=current_user.id,
            caminho_imagem=foto_path
        )
        db.session.add(nova_foto)
        db.session.commit()
        return jsonify(success=True)
    
    return jsonify(success=False)
