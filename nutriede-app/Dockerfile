# Usa uma imagem oficial do Python como base
FROM python:3.11

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de dependências primeiro para otimizar o cache
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

# Expõe a porta que o Cloud Run usa (geralmente 8080)
EXPOSE 8080

# Comando para iniciar a aplicação com o Gunicorn
# Ele automaticamente usa a variável de ambiente $PORT fornecida pelo Cloud Run
# Aponta para o objeto 'app' dentro do arquivo 'wsgi.py'
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "1", "--threads", "8", "--timeout", "0", "wsgi:app"]