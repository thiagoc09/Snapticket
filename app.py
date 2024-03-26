# Dentro do seu arquivo onde a função create_app é definida, como app/__init__.py
from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    global migrate
    migrate = Migrate(app, db)

    # Importar os modelos aqui para que eles sejam conhecidos pelo Flask-Migrate
    from app import models

    # Aqui você pode registrar seus blueprints e outras configurações

    return app
