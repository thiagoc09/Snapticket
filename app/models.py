from . import db  # Importando a instância de SQLAlchemy criada em __init__.py
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

    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)

    # Relacionamentos
    fotos = db.relationship('FotoEvento', backref='usuario', lazy='dynamic')

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
    fotos_evento = db.relationship('FotoEvento', backref='evento', lazy='dynamic')
    

    def __repr__(self):
        return f'<Evento {self.nome_evento}>'

class FotoEvento(db.Model):
    __tablename__ = 'fotos_evento'

    id = db.Column(db.Integer, primary_key=True)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventos.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    caminho_foto = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    def __repr__(self):
        return f'<FotoEvento {self.id} do Evento {self.evento_id}>'
