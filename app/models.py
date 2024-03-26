# app/models.py
from . import db  # Importando a instância de SQLAlchemy criada em __init__.py

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    sobrenome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    cpf = db.Column(db.String(20), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    caminho_selfie = db.Column(db.String(120), nullable=True)  # Caminho para a imagem de selfie para reconhecimento facial
    

    # Relacionamentos
    fotos = db.relationship('Foto', backref='usuario', lazy='dynamic')

    def __repr__(self):
        return f'<Usuario {self.nome} {self.sobrenome}>'

class Evento(db.Model):
    __tablename__ = 'eventos'

    id = db.Column(db.Integer, primary_key=True)
    nome_evento = db.Column(db.String(120), nullable=False)
    data_evento = db.Column(db.DateTime, nullable=False)
    localizacao = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.Text, nullable=True)

    # Relacionamentos
    fotos = db.relationship('Foto', backref='evento', lazy='dynamic')

    def __repr__(self):
        return f'<Evento {self.nome_evento}>'

class Foto(db.Model):
    __tablename__ = 'fotos'

    id = db.Column(db.Integer, primary_key=True)
    evento_id = db.Column(db.Integer, db.ForeignKey('eventos.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    caminho_foto = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Foto {self.id} do Evento {self.evento_id}>'