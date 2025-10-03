# -*- coding: utf-8 -*-
"""
Script para gerenciar as migrações do banco de dados com o Flask-Migrate.
"""

from flask_migrate import upgrade
from nutriede import create_app
from nutriede.extensions import db

# Cria uma instância da aplicação para obter o contexto da aplicação
app = create_app()

# Este bloco é executado quando o script é chamado diretamente
if __name__ == '__main__':
    # O contexto da aplicação é necessário para que as extensões do Flask,
    # como o SQLAlchemy, saibam qual configuração de aplicação usar.
    with app.app_context():
        # O comando 'upgrade' aplica as migrações pendentes ao banco de dados.
        # É uma prática recomendada para manter o schema do banco de dados atualizado.
        print("Iniciando a migração do banco de dados...")
        upgrade()
        print("Migração do banco de dados concluída com sucesso!")