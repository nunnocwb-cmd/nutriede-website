# ==============================================================================
# 1. IMPORTAÇÕES DAS BIBLIOTECAS
# ==============================================================================
import os
import datetime
import getpass  # Para ler a senha de forma segura no terminal
from dotenv import load_dotenv
from flask import (Flask, render_template, request,
                   redirect, url_for, flash)
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin
from werkzeug.utils import secure_filename

# ==============================================================================
# 2. INICIALIZAÇÃO E CONFIGURAÇÕES DO APP
# ==============================================================================

# Carrega as variáveis de ambiente do arquivo .env (senhas, etc.)
load_dotenv()

# Cria a instância principal da aplicação Flask
app = Flask(__name__)

# --- Configurações do App ---
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Configurações do E-mail ---
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# ==============================================================================
# 3. INICIALIZAÇÃO DAS EXTENSÕES
# ==============================================================================

# Garante que a pasta de uploads exista no projeto
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicializa as extensões com a instância do app
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# ==============================================================================
# 4. MODELOS DO BANCO DE DADOS
# ==============================================================================

class User(db.Model, UserMixin):
    """Modelo para a tabela de usuários do sistema."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# ==============================================================================
# 5. CONFIGURAÇÃO DO FLASK-LOGIN
# ==============================================================================

@login_manager.user_loader
def load_user(user_id):
    """Função que o Flask-Login usa para recarregar o objeto do usuário."""
    return db.session.get(User, int(user_id))

# ==============================================================================
# 6. COMANDOS PERSONALIZADOS DE TERMINAL (CLI)
# ==============================================================================

@app.cli.command("create-user")
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

# ==============================================================================
# 7. ROTAS DA APLICAÇÃO (VIEWS)
# ==============================================================================

@app.context_processor
def inject_year():
    """Disponibiliza o ano atual para todos os templates (usado no rodapé)."""
    return {'current_year': datetime.date.today().year}

@app.route('/')
def home():
    """Rota para a página inicial."""
    return render_template('index.html')

@app.route('/login')
def login():
    """Rota para a página de login da área restrita."""
    return render_template('login.html')

@app.route('/empresa')
def empresa():
    """Rota para a página 'A Empresa'."""
    return render_template('empresa.html')

@app.route('/estrutura')
def estrutura():
    """Rota para a página 'Estrutura e Qualidade'."""
    return render_template('estrutura.html')

@app.route('/servicos')
def servicos():
    """Rota para a página 'Nossos Serviços'."""
    return render_template('servicos.html')

@app.route('/enviar-contato', methods=['POST'])
def enviar_contato():
    """Processa o envio de TODOS os formulários de contato da página inicial."""
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        msg = None
        
        try:
            if form_type == 'orcamento':
                # (Lógica para o formulário de orçamento...)
                nome = request.form.get('nome')
                empresa = request.form.get('empresa')
                # ... etc ...
                subject = f"Novo Pedido de Orçamento - {empresa}"
                body = "..." # Corpo do e-mail
                msg = Message(subject=subject, sender=('Nutriêde Website', app.config['MAIL_USERNAME']), recipients=['nutriede@nutriede.com.br'], body=body)

            elif form_type == 'fornecedor':
                # (Lógica para o formulário de fornecedor...)
                subject = "Novo Contato de Fornecedor"
                body = "..." # Corpo do e-mail
                msg = Message(subject=subject, sender=('Nutriêde Website', app.config['MAIL_USERNAME']), recipients=['nutriede@nutriede.com.br'], body=body)
                
            elif form_type == 'trabalhe_conosco':
                # (Lógica para o formulário trabalhe conosco...)
                subject = "Nova Candidatura Recebida"
                body = "..." # Corpo do e-mail
                msg = Message(subject=subject, sender=('Nutriêde Website', app.config['MAIL_USERNAME']), recipients=['nutriede@nutriede.com.br'], body=body)
                curriculo = request.files.get('curriculo')
                if curriculo:
                    filename = secure_filename(curriculo.filename)
                    msg.attach(filename, curriculo.content_type, curriculo.read())

            if msg:
                mail.send(msg)
                flash('Sua mensagem foi enviada com sucesso! Agradecemos o seu contato.', 'success')
            else:
                flash('Tipo de formulário desconhecido.', 'warning')

        except Exception as e:
            print(f"ERRO AO ENVIAR E-MAIL: {e}")
            flash('Ocorreu um erro ao enviar sua mensagem. Por favor, tente novamente.', 'danger')

        return redirect(url_for('home') + '#contato')

# ==============================================================================
# 8. EXECUÇÃO DO SERVIDOR
# ==============================================================================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

