# ==============================================================================
# 1. IMPORTAÇÕES DAS BIBLIOTECAS
# ==============================================================================
import os
import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename

# ==============================================================================
# 2. INICIALIZAÇÃO E CONFIGURAÇÕES DO APP
# ==============================================================================

# Carrega as variáveis de ambiente do arquivo .env (senhas, etc.)
load_dotenv()

# Cria a instância principal da aplicação Flask
app = Flask(__name__)

# --- Configurações do App ---
# Lê as configurações do e-mail a partir do arquivo .env
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Chave secreta necessária para o sistema de mensagens 'flash' funcionar
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24))

# Pasta para salvar currículos temporariamente antes de anexar ao e-mail
app.config['UPLOAD_FOLDER'] = 'uploads'

# Garante que a pasta de uploads exista no projeto
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicializa a extensão Flask-Mail com as configurações do app
mail = Mail(app)


# ==============================================================================
# 3. FUNÇÕES AUXILIARES (CONTEXT PROCESSORS)
# ==============================================================================

# Esta função injeta o ano atual em todos os templates
# para que o rodapé esteja sempre atualizado.
@app.context_processor
def inject_year():
    """Disponibiliza o ano atual para todos os templates."""
    return {'current_year': datetime.date.today().year}


# ==============================================================================
# 4. ROTAS DAS PÁGINAS (VIEWS)
# ==============================================================================

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
        # Identifica qual dos três formulários foi enviado
        form_type = request.form.get('form_type')
        msg = None

        try:
            # Lógica para o formulário de ORÇAMENTO
            if form_type == 'orcamento':
                nome = request.form.get('nome')
                empresa = request.form.get('empresa')
                # ... coleta os outros campos ...
                subject = f"Novo Pedido de Orçamento - {empresa}"
                body = f"""... corpo do e-mail de orçamento ..."""
                msg = Message(subject=subject, sender=('Nutriêde Website', app.config['MAIL_USERNAME']), recipients=['nutriede@nutriede.com.br'], body=body)

            # Lógica para o formulário de FORNECEDOR
            elif form_type == 'fornecedor':
                # ... coleta os campos de fornecedor ...
                subject = f"Novo Contato de Fornecedor - ..."
                body = f"""... corpo do e-mail de fornecedor ..."""
                msg = Message(subject=subject, sender=('Nutriêde Website', app.config['MAIL_USERNAME']), recipients=['nutriede@nutriede.com.br'], body=body)

            # Lógica para o formulário TRABALHE CONOSCO
            elif form_type == 'trabalhe_conosco':
                candidato_nome = request.form.get('candidato_nome')
                curriculo = request.files.get('curriculo')
                # ... coleta os outros campos ...

                subject = f"Nova Candidatura Recebida - {candidato_nome}"
                body = f"""... corpo do e-mail de candidatura ..."""
                msg = Message(subject=subject, sender=('Nutriêde Website', app.config['MAIL_USERNAME']), recipients=['nutriede@nutriede.com.br'], body=body)

                # Anexa o currículo ao e-mail, se ele foi enviado
                if curriculo and curriculo.filename != '':
                    filename = secure_filename(curriculo.filename)
                    msg.attach(filename, curriculo.content_type, curriculo.read())

            # Envia o e-mail se um foi preparado
            if msg:
                mail.send(msg)
                flash('Sua mensagem foi enviada com sucesso! Agradecemos o seu contato.', 'success')
            else:
                flash('Tipo de formulário desconhecido.', 'warning')

        except Exception as e:
            # Em caso de erro, imprime no terminal para depuração
            print(f"ERRO AO ENVIAR E-MAIL: {e}")
            flash('Ocorreu um erro ao enviar sua mensagem. Por favor, tente novamente.', 'danger')

        # Redireciona o usuário de volta para a seção de contato da home
        return redirect(url_for('home') + '#contato')


# ==============================================================================
# 5. EXECUÇÃO DO SERVIDOR
# ==============================================================================

# Este bloco só é executado quando o arquivo é rodado diretamente (python app.py)
if __name__ == '__main__':
    # Usa a porta definida pelo ambiente de produção (Google Cloud) ou 8080 para testes locais
    port = int(os.environ.get("PORT", 8080))
    # Executa o app. debug=False é essencial para produção.
    app.run(host='0.0.0.0', port=port, debug=False)
