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
# Funções adicionadas para o sistema de login
from flask_login import (LoginManager, UserMixin, login_user,
                       logout_user, login_required, current_user)
from werkzeug.utils import secure_filename

# ==============================================================================
# 2. INICIALIZAÇÃO E CONFIGURAÇÕES DO APP
# ==============================================================================

# Carrega as variáveis de ambiente do arquivo .env (senhas, etc.)
load_dotenv()

# Cria a instância principal da aplicação Flask
app = Flask(__name__)

# --- Configurações Gerais ---
# Define a chave secreta, essencial para a segurança da sessão
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    print("AVISO: A variável de ambiente SECRET_KEY não está definida. Usando uma chave padrão para desenvolvimento.")
    SECRET_KEY = 'uma-chave-secreta-temporaria-e-insegura-para-desenvolvimento'
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Configuração do Banco de Dados ---
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("AVISO: A variável de ambiente DATABASE_URL não está definida. Usando um banco de dados SQLite local para desenvolvimento.")
    # Define o caminho absoluto para o banco de dados na raiz do projeto
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'local_test.db')
    DATABASE_URL = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

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
# Configurações do Flask-Login
login_manager.login_view = 'login'  # Página para onde redirecionar se não estiver logado
login_manager.login_message_category = 'info'
login_manager.login_message = "Por favor, faça login para aceder a esta página."

# ==============================================================================
# 4. MODELOS DO BANCO DE DADOS
# ==============================================================================

class User(db.Model, UserMixin):
    """Modelo para a tabela de utilizadores do sistema."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(80), nullable=False, default='user')

    def __repr__(self):
        return f'<User {self.username}>'

# ==============================================================================
# 5. CONFIGURAÇÃO DO FLASK-LOGIN
# ==============================================================================

@login_manager.user_loader
def load_user(user_id):
    """Função que o Flask-Login usa para recarregar o objeto do utilizador."""
    return db.session.get(User, int(user_id))

# ==============================================================================
# 6. COMANDOS PERSONALIZADOS DE TERMINAL (CLI)
# ==============================================================================

@app.cli.command("create-user")
def create_user():
    """Cria um novo utilizador administrador no sistema."""
    print("--- Criar Novo Utilizador Admin ---")
    username = input("Digite o nome de utilizador: ")
    email = input("Digite o e-mail do utilizador: ")
    password = getpass.getpass("Digite a senha: ")
    confirm_password = getpass.getpass("Confirme a senha: ")

    if password != confirm_password:
        print("As senhas não coincidem. Operação cancelada.")
        return

    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing_user:
        print("Erro: Já existe um utilizador com esse nome ou e-mail.")
        return

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password_hash=hashed_password, role='manager')

    db.session.add(new_user)
    db.session.commit()
    print(f"Utilizador '{username}' com a função 'manager' criado com sucesso!")

# ==============================================================================
# 7. ROTAS DA APLICAÇÃO (VIEWS)
# ==============================================================================

@app.context_processor
def inject_year():
    """Disponibiliza o ano atual para todos os templates (usado no rodapé)."""
    return {'current_year': datetime.date.today().year}


# --- Rotas Públicas ---

@app.route('/')
def home():
    """Rota para a página inicial."""
    return render_template('index.html')


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


# --- Rotas de Autenticação e Área Restrita ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Rota para a página de login e processamento do formulário."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            if user.role != 'manager':
                flash('Acesso negado. Apenas gestores podem entrar nesta área.', 'danger')
                return redirect(url_for('login'))
            
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login inválido. Verifique o e-mail e a senha.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Rota para fazer logout do utilizador."""
    logout_user()
    return redirect(url_for('home'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Rota para o painel de controlo, acessível apenas a utilizadores logados."""
    return render_template('dashboard.html')


# --- Rota do Formulário de Contato ---

@app.route('/enviar-contato', methods=['POST'])
def enviar_contato():
    """Processa o envio de TODOS os formulários de contato da página inicial."""
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        msg = None

        try:
            # --- Validação Unificada ---
            required_fields = []
            if form_type == 'orcamento':
                required_fields = ['nome', 'empresa', 'cnpj', 'qtd_refeicoes', 'email', 'mensagem']
            elif form_type == 'fornecedor':
                required_fields = ['fornecedor_empresa', 'fornecedor_contato', 'fornecedor_email', 'fornecedor_produto']
            elif form_type == 'trabalhe_conosco':
                required_fields = ['candidato_nome', 'candidato_email', 'candidato_telefone']

            # Verifica se os campos de texto estão preenchidos
            for field in required_fields:
                if not request.form.get(field):
                    flash('Por favor, preencha todos os campos obrigatórios.', 'warning')
                    return redirect(url_for('home') + '#contato')

            # Validação específica para o upload de arquivo
            if form_type == 'trabalhe_conosco':
                if 'curriculo' not in request.files or request.files['curriculo'].filename == '':
                    flash('Por favor, anexe o seu currículo.', 'warning')
                    return redirect(url_for('home') + '#contato')

            # --- Processamento do Formulário (se a validação passar) ---
            if form_type == 'orcamento':
                nome = request.form.get('nome')
                empresa = request.form.get('empresa')
                cnpj = request.form.get('cnpj')
                qtd_refeicoes = request.form.get('qtd_refeicoes')
                email = request.form.get('email')
                mensagem = request.form.get('mensagem')

                subject = f"Novo Pedido de Orçamento - {empresa}"
                body = f"""
                Novo pedido de ORÇAMENTO recebido pelo site:

                Nome: {nome}
                Empresa: {empresa}
                CNPJ: {cnpj}
                Nº de Refeições/Dia: {qtd_refeicoes}
                E-mail: {email}
                Mensagem: {mensagem}
                """
                msg = Message(subject=subject, sender=('Nutriêde Website', app.config['MAIL_USERNAME']), recipients=['nutriede@nutriede.com.br'], body=body)

            elif form_type == 'fornecedor':
                fornecedor_empresa = request.form.get('fornecedor_empresa')
                fornecedor_contato = request.form.get('fornecedor_contato')
                fornecedor_email = request.form.get('fornecedor_email')
                fornecedor_produto = request.form.get('fornecedor_produto')

                subject = f"Novo Contato de Fornecedor - {fornecedor_empresa}"
                body = f"""
                Novo contato de FORNECEDOR recebido pelo site:
                
                Nome da Empresa: {fornecedor_empresa}
                Nome do Contato: {fornecedor_contato}
                E-mail: {fornecedor_email}
                Produto/Serviço: {fornecedor_produto}
                """
                msg = Message(subject=subject, sender=('Nutriêde Website', app.config['MAIL_USERNAME']), recipients=['nutriede@nutriede.com.br'], body=body)

            elif form_type == 'trabalhe_conosco':
                candidato_nome = request.form.get('candidato_nome')
                candidato_email = request.form.get('candidato_email')
                candidato_telefone = request.form.get('candidato_telefone')
                curriculo = request.files.get('curriculo')

                subject = f"Nova Candidatura Recebida - {candidato_nome}"
                body = f"""
                Nova candidatura para 'TRABALHE CONOSCO' recebida pelo site:

                Nome Completo: {candidato_nome}
                E-mail: {candidato_email}
                Telefone: {candidato_telefone}
                
                O currículo está em anexo.
                """
                msg = Message(subject=subject, sender=('Nutriêde Website', app.config['MAIL_USERNAME']), recipients=['nutriede@nutriede.com.br'], body=body)
                
                # O anexo é adicionado aqui, pois a validação já garantiu que ele existe
                filename = secure_filename(curriculo.filename)
                msg.attach(filename, curriculo.content_type, curriculo.read())

            if msg:
                mail.send(msg)
                flash('Sua mensagem foi enviada com sucesso! Agradecemos o seu contato.', 'success')
            else:
                # Esta condição agora é menos provável de ser atingida, mas é mantida por segurança
                flash('Tipo de formulário desconhecido.', 'warning')

        except Exception as e:
            print(f"ERRO AO ENVIAR E-MAIL: {e}")
            flash('Ocorreu um erro ao enviar sua mensagem. Por favor, tente novamente.', 'danger')

        return redirect(url_for('home') + '#contato')

# ==============================================================================
# 8. EXECUÇÃO DO SERVIDOR
# ==============================================================================

if __name__ == '__main__':
    # Usa a porta definida pelo ambiente de produção ou 8080 para testes locais
    port = int(os.environ.get("PORT", 8080))
    # Executa o app. debug=False é essencial para produção.
    app.run(host='0.0.0.0', port=port, debug=False)