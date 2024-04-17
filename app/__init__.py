from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
import os

# Instâncias globais do SQLAlchemy e Migrate
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicialização dos plugins
    db.init_app(app)
    migrate.init_app(app, db)

    # Configuração do LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)


    # Certifique-se que as pastas para uploads sejam criadas
    for folder in [app.config['UPLOAD_FOLDER'], 
                   app.config['USER_SELFIES_FOLDER'], 
                   app.config['EVENT_COVERS_FOLDER']]:
        if not os.path.exists(folder):
            os.makedirs(folder)


    # Função para carregar o usuário a partir da sessão
    from app.models import Usuario  # Import aqui para evitar importação circular
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Registro dos blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
