# -*- coding: utf-8 -*-
"""Modelos do banco de dados da aplicação."""

from flask_login import UserMixin
from .extensions import db

class User(db.Model, UserMixin):
    """Modelo para a tabela de usuários do sistema."""
    __tablename__ = 'user'  # Definindo o nome da tabela explicitamente

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'