# -*- coding: utf-8 -*-
"""Inicializa as extensões do Flask para serem usadas na aplicação."""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_login import LoginManager

# Instâncias das extensões
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
mail = Mail()
login_manager = LoginManager()

# Configurações do Flask-Login
login_manager.login_view = 'sistema.login'  # Aponta para a rota de login no blueprint 'sistema'
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = 'info'