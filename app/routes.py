# app/routes.py
from flask import render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from .models import Usuario
from . import db
import os
from . import main

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/')
def home():
    return render_template('login.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pass
    return render_template('login.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome')
        sobrenome = request.form.get('sobrenome')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        cpf = request.form.get('cpf')
        senha = request.form.get('senha')
        senha_hash = generate_password_hash(senha)
        
        selfie = request.files.get('selfie')
        if selfie and allowed_file(selfie.filename):
            filename = secure_filename(selfie.filename)
            selfie_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            selfie.save(selfie_path)
        else:
            flash('Tipo de arquivo não permitido.')
            return redirect(request.url)
        
        novo_usuario = Usuario(
            nome=nome,
            sobrenome=sobrenome,
            email=email,
            telefone=telefone,
            cpf=cpf,
            senha_hash=senha_hash,
            caminho_selfie=selfie_path
        )
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        return redirect(url_for('home'))
    return render_template('register.html')
