# config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://snapticket1:047441cc-1b6e-4aa4-b679-a2ecf4fa64d1@snapticket.c128ww4a4ihw.us-east-1.rds.amazonaws.com:5432/snapticket'  

    UPLOAD_FOLDER = os.path.join('app','static', 'uploads')
    USER_SELFIES_FOLDER = os.path.join(UPLOAD_FOLDER, 'user_selfies')
    EVENT_COVERS_FOLDER = os.path.join(UPLOAD_FOLDER, 'event_covers')
    EVENT_IMAGES_FOLDER = os.path.join(UPLOAD_FOLDER, 'event_images')
    DEFAULT_EVENT_COVER = os.path.join('images', 'eventos', 'default_cover.jpg')
    SECRET_KEY = 'snapticket123'
    #SECRET_KEY = os.environ.get('SECRET_KEY') or 'snapticket'
#    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False