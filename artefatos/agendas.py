import sqlite3
from flask import Flask, request , jsonify
from flasgger import Swagger
from flask_cors import CORS
import os

app = Flask(__name__)

CORS(app)  

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "swagger",
            "route": "/apidocs.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/",
    "info": {
        "title": "API para Controle de Agenda dos Clientes",
        "description": "Documentação da API para Controle de Agenda",
        "version": "1.0",
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    },
   "lang": "pt-br"  # Define o idioma como Português do Brasil
}

Swagger(app, config=swagger_config)

DATABASE = 'database/db_agenda.db'


def connect_db():
    """Conecta ao banco de dados SQLite, criando-o caso não exista."""
    if not os.path.exists(os.path.dirname(DATABASE)):
        os.makedirs(os.path.dirname(DATABASE), exist_ok=True)  # Cria o diretório, se necessário

    return sqlite3.connect(DATABASE)

def create_table():
    """Cria a tabela eventos no banco de dados, caso ainda não exista."""
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT NOT NULL,
                dataInicio TEXT CHECK(dataInicio LIKE '____-__-__ __:__') NOT NULL,
                dataFim TEXT CHECK(dataFim LIKE '____-__-__ __:__') NOT NULL,
                local TEXT NOT NULL,
                estadoAtualAgenda TEXT CHECK(estadoAtualAgenda IN ('RECEBIDO', 'CONFIRMADO', 'ATENDIDO', 'CANCELADO')) NOT NULL
            )
        ''')
        conn.commit()    

@app.route('/eventos', methods=['GET'])
def get_eventos():
    """Retorna todos os Eventos
    ---
    responses:
      200:
        description: Uma lista de Eventos
    """
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM eventos')
        colunas = [desc[0] for desc in cursor.description]
        eventos = [dict(zip(colunas, row)) for row in cursor.fetchall()]
        return jsonify(eventos)
    
@app.route('/eventos', methods=['POST'])
def create_eventos():
    """Insere um novo Evento
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            titulo:
                type: string
            descricao:
                type: string
            dataInicio:
                type: string
            dataFim:
                type: string
            local:
                type: string
            estadoAtualAgenda:
                type: string
    responses:
      201:
        description: Evento criado com sucesso
      400:
        description: Erro ao criar evento
    """
    data = request.json
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO eventos (titulo, descricao, dataInicio, dataFim, local, estadoAtualAgenda) VALUES (?, ?, ?, ?, ?, ?)", 
                        (data['titulo'], data['descricao'], data['dataInicio'], data['dataFim'], data['local'], data['estadoAtualAgenda']))
            conn.commit()
        return jsonify({"message": "Evento criado com sucesso!"}), 201
    except sqlite3.Error as e:
        return jsonify({"error": "Erro ao criar evento", "details": str(e)}), 400

@app.route('/eventos/<int:evento_id>', methods=['GET'])
def get_evento(evento_id):
    """Busca um evento pelo ID
    ---
    parameters:
      - name: evento_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Dados do Evento
      404:
        description: Evento não encontrado
    """
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM eventos WHERE id = ?", (evento_id,))
        evento = cursor.fetchone()
        if evento:
            colunas = [desc[0] for desc in cursor.description]
            evento_dict = dict(zip(colunas, evento))
            return jsonify(evento_dict)
        
    return (jsonify({"error": "Evento não encontrado"}), 404)

@app.route('/eventos/<int:evento_id>', methods=['PUT'])
def update_evento(evento_id):
    """Atualiza as informações do Evento
    ---
    parameters:
      - name: evento_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            titulo:
                type: string
            descricao:
                type: string
            dataInicio:
                type: string
            dataFim:
                type: string
            local:
                type: string
            estadoAtualAgenda:
                type: string
    responses:
      200:
        description: Evento atualizado com sucesso
      404:
        description: Evento não encontrado
      400:
        description: Erro ao atualizar evento

    """
    data = request.json
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE eventos SET titulo = ?, descricao = ?, dataInicio = ?, dataFim = ?, local = ?, estadoAtualAgenda = ? WHERE id = ?", 
                        (data['titulo'], data['descricao'], data['dataInicio'], data['dataFim'], data['local'], data['estadoAtualAgenda'], evento_id))
            if cursor.rowcount == 0:
                return jsonify({"error": "Evento não encontrado"}), 404
            conn.commit()
        return jsonify({"message": "Evento atualizado com sucesso!"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": "Erro ao atualizar evento", "details": str(e)}), 400

@app.route('/eventos/<int:evento_id>', methods=['DELETE'])
def delete_evento(evento_id):
    """Exclui um evento pelo ID
    ---
    parameters:
      - name: evento_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Evento excluído com sucesso
      404:
        description: Evento não encontrado
      400:
        description: Erro ao excluir evento        
    """
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM eventos WHERE id = ?", (evento_id,))
            if cursor.rowcount == 0:
                return jsonify({"error": "Evento não encontrado"}), 404
            conn.commit()
        return jsonify({"message": "Evento excluído com sucesso!"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": "Erro ao excluir evento", "details": str(e)}), 400

@app.route('/eventos/status/<int:evento_id>', methods=['PUT'])
def update_status_evento(evento_id):
    """Atualiza o status do Evento
    ---
    parameters:
      - name: evento_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            estadoAtualAgenda:
                type: string
    responses:
      200:
        description: Status do Evento atualizado com sucesso
      404:
        description: Evento não encontrado
      400:
        description: Erro ao atualizar status do evento
    """
    data = request.json
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE eventos SET estadoAtualAgenda = ? WHERE id = ?", (data['estadoAtualAgenda'], evento_id))
            if cursor.rowcount == 0:
                return jsonify({"error": "Evento não encontrado"}), 404
            conn.commit()
        return jsonify({"message": "Status do Evento atualizado com sucesso!"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": "Erro ao atualizar status do evento", "details": str(e)}), 400

if __name__ == '__main__':
    create_table()
    app.run(host='0.0.0.0', port=5000, debug=True)
# End of agendas.py