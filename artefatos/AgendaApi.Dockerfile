# Usa uma imagem base do Python
FROM python:3.9

# Define um volume para persistência
VOLUME /var/www/html/agendas-api

# Define o diretório de trabalho
WORKDIR /var/www/html/agendas-api

# Copia os arquivos para o contêiner
COPY agendas.py /var/www/html/agendas-api

# Copia e instala as dependências a partir do requirements.txt
COPY requerimentos.txt .
RUN pip install --no-cache-dir -r requerimentos.txt

# Expõe a porta usada pela API
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["python", "agendas.py"]

