from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    caminho_selfie = db.Column(db.String(120), nullable=True)  # Caminho para a imagem de selfie
    
    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)

    def __repr__(self):
        return f'<Usuario {self.nome}>'
    
class Evento(db.Model):
    __tablename__ = 'eventos'

    id = db.Column(db.Integer, primary_key=True)
    nome_evento = db.Column(db.String(120), nullable=False)
    data_evento = db.Column(db.DateTime, nullable=False)
    foto_capa = db.Column(db.String(120), nullable=True)  # Caminho para a foto de capa do evento
    plano_tipo = db.Column(db.String(50), nullable=False)  # Adicionado para guardar o tipo de plano ('monetize' ou 'impulsione')
    
    # Relacionamentos
    fotos_evento = db.relationship('Foto', backref='evento', lazy='dynamic')

class Foto(db.Model):
    __tablename__ = 'fotos'

    id = db.Column(db.Integer, primary_key=True)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventos.id'), nullable=False)
    caminho_foto = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    sem_marca_dagua = db.Column(db.Boolean, default=False)  # Indica se a foto deve ter marca d'água ou não
    
    # Relacionamento com a tabela de associação
    participantes = db.relationship('FotoUsuario', backref='foto', lazy='dynamic')

    def __repr__(self):
        return f'<Foto {self.id} do Evento {self.evento_id}>'

class FotoUsuario(db.Model):
    __tablename__ = 'fotos_usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    foto_id = db.Column(db.Integer, db.ForeignKey('fotos.id'))
    
    def __repr__(self):
        return f'<FotoUsuario {self.usuario_id} - Foto {self.foto_id}>'

class Compra(db.Model):
    __tablename__ = 'compras'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    foto_id = db.Column(db.Integer, db.ForeignKey('fotos.id'))
    data_compra = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Compra {self.usuario_id} - Foto {self.foto_id}>'

class ImagemEvento(db.Model):
    __tablename__ = 'imagens_evento'

    id = db.Column(db.Integer, primary_key=True)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventos.id'), nullable=False)
    caminho_imagem = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<ImagemEvento {self.id} do Evento {self.evento_id}>'

class FotosGaleria(db.Model):
    __tablename__ = 'fotos_galeria'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    caminho_imagem = db.Column(db.String(255), nullable=False)
    data_adicao = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('Usuario', back_populates='fotos_galeria')

Usuario.fotos_galeria = db.relationship('FotosGaleria', order_by=FotosGaleria.id, back_populates='user')
