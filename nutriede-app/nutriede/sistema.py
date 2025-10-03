# -*- coding: utf-8 -*-
"""Blueprint para as rotas do sistema interno (dashboard, login, etc.)."""

import getpass
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash)
from flask_login import login_user, logout_user, login_required, current_user

from .extensions import db, bcrypt
from .models import User

# Criação do Blueprint para o sistema
sistema_bp = Blueprint('sistema', __name__, url_prefix='/sistema')

# ==============================================================================
# ROTAS DE AUTENTICAÇÃO E ÁREA RESTRITA
# ==============================================================================

@sistema_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rota para a página de login e processamento do formulário."""
    if current_user.is_authenticated:
        return redirect(url_for('sistema.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            # Redireciona para o dashboard ou para a página 'next' se ela existir
            return redirect(next_page or url_for('sistema.dashboard'))
        else:
            flash('Login inválido. Verifique o e-mail e a senha.', 'danger')

    return render_template('login.html')


@sistema_bp.route('/logout')
@login_required
def logout():
    """Rota para fazer logout do usuário."""
    logout_user()
    flash('Você foi desconectado com sucesso.', 'success')
    return redirect(url_for('site.home'))


@sistema_bp.route('/dashboard')
@login_required
def dashboard():
    """Rota para o painel de controle, acessível apenas a usuários logados."""
    return render_template('dashboard.html')

# ==============================================================================
# COMANDOS PERSONALIZADOS DE TERMINAL (CLI)
# ==============================================================================

@sistema_bp.cli.command("create-user")
def create_user():
    """Cria um novo usuário administrador no sistema."""
    print("--- Criar Novo Usuário Admin ---")
    username = input("Digite o nome de usuário: ")
    email = input("Digite o e-mail do usuário: ")
    password = getpass.getpass("Digite a senha: ")
    confirm_password = getpass.getpass("Confirme a senha: ")

    if password != confirm_password:
        print("As senhas não coincidem. Operação cancelada.")
        return

    # Usando with db.session.no_autoflush: para evitar problemas de flush
    with db.session.no_autoflush:
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

    if existing_user:
        print("Erro: Já existe um usuário com esse nome ou e-mail.")
        return

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password_hash=hashed_password)

    db.session.add(new_user)
    db.session.commit()
    print(f"Usuário '{username}' criado com sucesso!")