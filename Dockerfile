# Usa a versão padrão e completa do Python 3.11
FROM python:3.11

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia apenas o ficheiro de dependências da aplicação para o contêiner
COPY nutriede-app/requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação (de dentro de nutriede-app) para o contêiner
COPY nutriede-app/ .

# Expõe a porta 8000, que a nossa aplicação vai usar internamente
EXPOSE 8000

# Comando para iniciar a aplicação com o Gunicorn, usando o caminho absoluto.
CMD ["/usr/local/bin/gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "8", "--timeout", "0", "app:app"]

