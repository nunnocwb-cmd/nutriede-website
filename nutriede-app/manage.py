import os
from flask_migrate import Migrate, upgrade
from app import app, db  # Importa a nossa app e a instância db do nosso ficheiro principal
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do ficheiro .env
load_dotenv()

# Inicializa o Migrate com a nossa app e o db
migrate = Migrate(app, db)

# Este bloco permite-nos correr o script diretamente
if __name__ == '__main__':
    # Este é um truque para garantir que o contexto da aplicação esteja ativo
    # para que as extensões do Flask funcionem corretamente.
    with app.app_context():
        # O comando 'upgrade' é o mais importante, aplica as migrações.
        # Estamos a chamá-lo diretamente via Python.
        upgrade()
        print("Migração do banco de dados concluída com sucesso!")
