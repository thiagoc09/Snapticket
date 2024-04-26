from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    cpf = db.Column(db.String(20), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    caminho_selfie = db.Column(db.String(120), nullable=True)  # Caminho para a imagem de selfie
    
    # Relacionamentos
    fotos_usuario = db.relationship('FotoUsuario', backref='usuario', lazy='dynamic')
    compras = db.relationship('Compra', backref='usuario', lazy='dynamic')

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
    localizacao = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    foto_capa = db.Column(db.String(120), nullable=True)  # Caminho para a foto de capa do evento
    
    # Relacionamentos
    fotos_evento = db.relationship('Foto', backref='evento', lazy='dynamic')

    def __repr__(self):
        return f'<Evento {self.nome_evento}>'

class Foto(db.Model):
    __tablename__ = 'fotos'

    id = db.Column(db.Integer, primary_key=True)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventos.id'), nullable=False)
    caminho_foto = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    # Relacionamento com a tabela de associação
    participantes = db.relationship('FotoUsuario', backref='foto', lazy='dynamic')

    def __repr__(self):
        return f'<Foto {self.id} do Evento {self.evento_id}>'

class FotoUsuario(db.Model):
    __tablename__ = 'fotos_usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    foto_id = db.Column(db.Integer, db.ForeignKey('fotos.id'))
    
    # Poderia adicionar campos adicionais aqui, como confirmação de reconhecimento facial

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