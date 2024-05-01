# config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
  

    UPLOAD_FOLDER = os.path.join('app','static', 'uploads')
    USER_SELFIES_FOLDER = os.path.join(UPLOAD_FOLDER, 'user_selfies')
    EVENT_COVERS_FOLDER = os.path.join(UPLOAD_FOLDER, 'event_covers')
    EVENT_IMAGES_FOLDER = os.path.join(UPLOAD_FOLDER, 'event_images')
    DEFAULT_EVENT_COVER = os.path.join('images', 'eventos', 'default_cover.jpg')

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'snapticket'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False