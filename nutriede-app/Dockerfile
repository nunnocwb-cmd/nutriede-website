# Usa a versão padrão e completa do Python 3.11
FROM python:3.11

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de dependências para o contêiner
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da aplicação para o contêiner
COPY . .

# Expõe a porta 8000, que a nossa aplicação vai usar internamente
EXPOSE 8000

# Comando para iniciar a aplicação com o Gunicorn
CMD ["/usr/local/bin/gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "8", "--timeout", "0", "app:app"]

