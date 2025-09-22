import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import datetime

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Disponibiliza o ano atual para todos os templates
@app.context_processor
def inject_year():
    return {'current_year': datetime.date.today().year}

# --- Configuração do Flask-Mail ---
# Lê as configurações do arquivo .env de forma segura
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Chave secreta para usar o sistema de mensagens "flash"
app.config['SECRET_KEY'] = os.urandom(24)

# Inicia a extensão Mail com as configurações do app
mail = Mail(app)


# --- Rotas da Aplicação ---

# Duas linhas em branco para separar as funções
@app.route('/')
def home():
    """Rota para a página inicial."""
    return render_template('index.html')
# Duas linhas em branco para separar as funções

@app.route('/empresa')
def empresa():
    """Rota para a página 'A Empresa'."""
    return render_template('empresa.html')


# Duas linhas em branco para separar

@app.route('/estrutura')
def estrutura():
    """Rota para a página 'Estrutura e Qualidade'."""
    return render_template('estrutura.html')

@app.route('/servicos')
def servicos():
    """Rota para a página 'Nossos Serviços'."""
    return render_template('servicos.html')


# Duas linhas em branco para separar as funções
@app.route('/enviar-contato', methods=['POST'])
def enviar_contato():
    """Processa o envio do formulário de contato."""
    if request.method == 'POST':
        nome = request.form.get('nome')
        empresa = request.form.get('empresa')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        mensagem = request.form.get('mensagem')

        corpo_email = f"""
        Novo pedido de proposta recebido pelo site:

        Nome: {nome}
        Empresa: {empresa}
        E-mail: {email}
        Telefone: {telefone}

        Mensagem:
        {mensagem}
        """

        try:
            msg = Message(
                subject=f"Novo Contato do Site - {empresa}",
                sender=('Nutriêde Website', app.config['MAIL_USERNAME']),
                recipients=['nutriede@nutriede.com.br'],
                body=corpo_email
            )
            mail.send(msg)
            flash(
                'Sua mensagem foi enviada com sucesso! '
                'Entraremos em contato em breve.', 'success'
            )
        except Exception as e:
            # Imprime o erro detalhado no terminal para depuração
            print(f"ERRO AO ENVIAR E-MAIL: {e}")
            flash(
                'Ocorreu um erro ao enviar sua mensagem. '
                'Por favor, tente novamente.', 'danger'
            )

        return redirect(url_for('home') + '#contato')


if __name__ == '__main__':
    # O Cloud Run define a porta através de uma variável de ambiente 'PORT'.
    # Usamos 8080 como padrão se a variável não for encontrada (para testes locais).
    port = int(os.environ.get("PORT", 8080))
    # O debug=False é crucial para ambientes de produção.
    app.run(host='0.0.0.0', port=port, debug=False)


# Linha em branco no final do arquivo