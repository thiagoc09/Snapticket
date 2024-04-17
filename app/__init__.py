from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  # Especifica a rota de login para redirecionar usuários não autenticados

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(app.config['USER_SELFIES_FOLDER']):
        os.makedirs(app.config['USER_SELFIES_FOLDER'])
    if not os.path.exists(app.config['EVENT_COVERS_FOLDER']):
        os.makedirs(app.config['EVENT_COVERS_FOLDER'])

    db.init_app(app)
    migrate.init_app(app, db)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app import models  # Importe os modelos aqui

    return app