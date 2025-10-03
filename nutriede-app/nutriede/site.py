# -*- coding: utf-8 -*-
"""Blueprint para as rotas públicas do site da Nutriêde."""

import datetime
from flask import (Blueprint, render_template, request,
                   redirect, url_for, flash, current_app)
from flask_mail import Message
from werkzeug.utils import secure_filename

from .extensions import mail

# Criação do Blueprint para o site
site_bp = Blueprint('site', __name__)

# ==============================================================================
# CONTEXT PROCESSOR PARA O ANO ATUAL
# ==============================================================================

@site_bp.app_context_processor
def inject_year():
    """Disponibiliza o ano atual para todos os templates (usado no rodapé)."""
    return {'current_year': datetime.date.today().year}

# ==============================================================================
# ROTAS PÚBLICAS
# ==============================================================================

@site_bp.route('/')
def home():
    """Rota para a página inicial."""
    return render_template('index.html')


@site_bp.route('/empresa')
def empresa():
    """Rota para a página 'A Empresa'."""
    return render_template('empresa.html')


@site_bp.route('/estrutura')
def estrutura():
    """Rota para a página 'Estrutura e Qualidade'."""
    return render_template('estrutura.html')


@site_bp.route('/servicos')
def servicos():
    """Rota para a página 'Nossos Serviços'."""
    return render_template('servicos.html')

# ==============================================================================
# ROTA DO FORMULÁRIO DE CONTATO
# ==============================================================================

@site_bp.route('/enviar-contato', methods=['POST'])
def enviar_contato():
    """Processa o envio de TODOS os formulários de contato da página inicial."""
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        msg = None

        try:
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
                msg = Message(subject=subject, sender=('Nutriêde Website', current_app.config['MAIL_USERNAME']), recipients=['nutriede@nutriede.com.br'], body=body)

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
                msg = Message(subject=subject, sender=('Nutriêde Website', current_app.config['MAIL_USERNAME']), recipients=['nutriede@nutriede.com.br'], body=body)

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
                msg = Message(subject=subject, sender=('Nutriêde Website', current_app.config['MAIL_USERNAME']), recipients=['nutriede@nutriede.com.br'], body=body)

                if curriculo and curriculo.filename != '':
                    filename = secure_filename(curriculo.filename)
                    msg.attach(filename, curriculo.content_type, curriculo.read())

            if msg:
                mail.send(msg)
                flash('Sua mensagem foi enviada com sucesso! Agradecemos o seu contato.', 'success')
            else:
                flash('Tipo de formulário desconhecido.', 'warning')

        except Exception as e:
            # Usar o logger da aplicação para registrar o erro
            current_app.logger.error(f"ERRO AO ENVIAR E-MAIL: {e}")
            flash('Ocorreu um erro ao enviar sua mensagem. Por favor, tente novamente.', 'danger')

        # Redireciona para a seção de contato da home
        return redirect(url_for('site.home') + '#contato')