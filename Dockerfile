FROM
python:3.10
# Usando uma imagem oficial do Python
FROM python:3.10

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de dependências
COPY requirements.txt requirements.txt

# Instala as dependências
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia os arquivos do projeto para o container
COPY . .

# Exposição da porta 8080, usada pelo Flask no Cloud Run
EXPOSE 8080

# Comando para iniciar o servidor Flask com Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "run:app"]
