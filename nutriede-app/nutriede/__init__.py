# -*- coding: utf-8 -*-
"""Ponto de entrada da aplicação e 'Application Factory'."""

import os
from dotenv import load_dotenv
from flask import Flask
import sqlalchemy

# Importações para o Cloud SQL Connector
from google.cloud.sql.connector import Connector, IPTypes

# Importações locais
from .extensions import db, migrate, bcrypt, mail, login_manager
from .models import User
from .site import site_bp
from .sistema import sistema_bp

def create_app():
    """
    Cria e configura uma instância da aplicação Flask.
    Este é o padrão 'Application Factory'.
    """
    # Carrega as variáveis de ambiente do arquivo .env
    load_dotenv()

    # Cria a instância principal da aplicação Flask
    app = Flask(__name__)

    # --- Configurações Gerais do App ---
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, '..', 'uploads')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- Configurações do E-mail ---
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

    # --- Configuração da Conexão com o Banco de Dados (Cloud SQL) ---
    def get_conn() -> sqlalchemy.engine.base.Connection:
        """Função que cria uma conexão segura com o Cloud SQL."""
        connector = Connector()
        instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]
        db_user = os.environ["DB_USER"]
        db_pass = os.environ["DB_PASS"]
        db_name = os.environ["DB_NAME"]
        ip_type = IPTypes.PRIVATE if os.environ.get("GOOGLE_CLOUD_RUN") else IPTypes.PUBLIC

        return connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=ip_type,
        )

    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+pg8000://"
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "creator": get_conn
    }

    # --- Inicialização das Extensões com o App ---
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    # Garante que a pasta de uploads exista
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # --- Configuração do User Loader para Flask-Login ---
    @login_manager.user_loader
    def load_user(user_id):
        """Função que o Flask-Login usa para recarregar o objeto do usuário."""
        return db.session.get(User, int(user_id))

    # --- Registro dos Blueprints ---
    app.register_blueprint(site_bp)
    app.register_blueprint(sistema_bp)

    return app