import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import datetime

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# --- Configurações ---
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads' # Pasta para salvar currículos temporariamente

# Garante que a pasta de uploads exista
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

mail = Mail(app)


# Disponibiliza o ano atual para todos os templates
@app.context_processor
def inject_year():
    return {'current_year': datetime.date.today().year}


# --- Rotas da Aplicação ---
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


@app.route('/enviar-contato', methods=['POST'])
def enviar_contato():
    """Processa o envio de TODOS os formulários de contato."""
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        msg = None
        
        try:
            if form_type == 'orcamento':
                # Coleta dados do formulário de orçamento
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
                # Coleta dados do formulário de fornecedor
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
                # Coleta dados do formulário de trabalhe conosco
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


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
    