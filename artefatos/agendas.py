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
   'language': 'pt-BR' # Define o idioma como Português do Brasil
}

app.config['SWAGGER'] = swagger_config  # Aplica a configuração

swagger = Swagger(app)

# Banco de Dados
DATABASE = 'database/db_agenda.db'

#Criação do Banco de Dados
def connect_db():
    """Conecta ao banco de dados SQLite, criando-o caso não exista."""
    if not os.path.exists(os.path.dirname(DATABASE)):
        os.makedirs(os.path.dirname(DATABASE), exist_ok=True)  # Cria o diretório, se necessário

    return sqlite3.connect(DATABASE)

#Criação da Tabela de Eventos no Banco de Dados
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

# Rotas

# Rota para listar todos os eventos
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
    
# Rota para criar um novo evento    
@app.route('/eventos', methods=['POST'])
def create_eventos():
    """Insere um novo Evento
    ---
    parameters:
      - name: titulo
        in: formData
        type: string
        required: true
        description: "Título do evento"
        example: "Lançamento do Sistema X"
      - name: descricao
        in: formData
        type: string
        required: true
        description: "Descrição do evento"
        example: "Evento de apresentação do novo sistema"
      - name: dataInicio
        in: formData
        type: string
        format: date-time
        required: true
        description: "Data e hora de início do evento"
        example: "2025-04-01 14:00"
      - name: dataFim
        in: formData
        type: string
        format: date-time
        required: true
        description: "Data e hora de término do evento"
        example: "2025-04-01 18:00"
      - name: local
        in: formData
        type: string
        required: true
        description: "Local do evento"
        example: "Auditório Central"
      - name: estadoAtualAgenda
        in: formData
        type: string
        required: true
        enum: ["RECEBIDO", "CONFIRMADO", "ATENDIDO", "CANCELADO"]
        description: "Estado atual da agenda do evento"
        example: "RECEBIDO"
    consumes:
      - application/x-www-form-urlencoded
    responses:
      201:
        description: Evento criado com sucesso
        content:
          application/json:
            example:
              message: "Evento criado com sucesso!"
      400:
        description: Erro ao criar evento
        content:
          application/json:
            example:
              error: "Erro ao criar evento"
              details: "Detalhes do erro"
    """
    data = request.form
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO eventos (titulo, descricao, dataInicio, dataFim, local, estadoAtualAgenda) VALUES (?, ?, ?, ?, ?, ?)",
                (data['titulo'], data['descricao'], data['dataInicio'], data['dataFim'], data['local'], data['estadoAtualAgenda'])
            )
            conn.commit()
        return jsonify({"message": "Evento criado com sucesso!"}), 201
    except sqlite3.Error as e:
        return jsonify({"error": "Erro ao criar evento", "details": str(e)}), 400


# Rota para buscar um evento pelo ID
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

# Rota para atualizar um evento pelo ID
@app.route('/eventos/<int:evento_id>', methods=['PUT'])
def update_evento(evento_id):
    """Atualiza as informações do Evento
    ---
    parameters:
      - name: evento_id
        in: path
        type: integer
        required: true
        description: "ID do evento a ser atualizado"
      - name: titulo
        in: formData
        type: string
        required: false
        description: "Novo título do evento"
        example: "Atualização do Sistema X"
      - name: descricao
        in: formData
        type: string
        required: false
        description: "Nova descrição do evento"
        example: "Nova versão do sistema será apresentada"
      - name: dataInicio
        in: formData
        type: string
        format: date-time
        required: false
        description: "Nova data e hora de início do evento"
        example: "2025-05-01 10:00:00"
      - name: dataFim
        in: formData
        type: string
        format: date-time
        required: false
        description: "Nova data e hora de término do evento"
        example: "2025-05-01 12:00:00"
      - name: local
        in: formData
        type: string
        required: false
        description: "Novo local do evento"
        example: "Sala de Reuniões 2"
      - name: estadoAtualAgenda
        in: formData
        type: string
        required: false
        enum: ["RECEBIDO", "CONFIRMADO", "ATENDIDO", "CANCELADO"]
        description: "Novo estado da agenda do evento"
        example: "RECEBIDO"
    consumes:
      - application/x-www-form-urlencoded
    responses:
      200:
        description: Evento atualizado com sucesso
        content:
          application/json:
            example:
              message: "Evento atualizado com sucesso!"
      404:
        description: Evento não encontrado
        content:
          application/json:
            example:
              error: "Evento não encontrado"
      400:
        description: Erro ao atualizar evento
        content:
          application/json:
            example:
              error: "Erro ao atualizar evento"
              details: "Detalhes do erro"
    """
    data = request.form
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE eventos SET titulo = COALESCE(?, titulo), descricao = COALESCE(?, descricao), "
                "dataInicio = COALESCE(?, dataInicio), dataFim = COALESCE(?, dataFim), "
                "local = COALESCE(?, local), estadoAtualAgenda = COALESCE(?, estadoAtualAgenda) "
                "WHERE id = ?", 
                (data.get('titulo'), data.get('descricao'), data.get('dataInicio'), 
                 data.get('dataFim'), data.get('local'), data.get('estadoAtualAgenda'), evento_id)
            )
            if cursor.rowcount == 0:
                return jsonify({"error": "Evento não encontrado"}), 404
            conn.commit()
        return jsonify({"message": "Evento atualizado com sucesso!"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": "Erro ao atualizar evento", "details": str(e)}), 400

# Rota para excluir um evento pelo ID
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

# Rota para atualizar o status do evento
@app.route('/eventos/status/<int:evento_id>', methods=['PUT'])
def update_status_evento(evento_id):
    """Atualiza o status do Evento
    ---
    parameters:
      - name: evento_id
        in: path
        type: integer
        required: true
        description: "ID do evento a ser atualizado"
        example: 1
      - name: estadoAtualAgenda
        in: formData
        type: string
        required: true
        enum: ["RECEBIDO", "CONFIRMADO", "ATENDIDO", "CANCELADO"]
        description: "Novo estado do evento"
        example: "CONFIRMADO"
    consumes:
      - application/x-www-form-urlencoded
    responses:
      200:
        description: Status do Evento atualizado com sucesso
        content:
          application/json:
            example:
              message: "Status do Evento atualizado com sucesso!"
              evento: 
                id: 1
                estadoAtualAgenda: "CONFIRMADO"
      404:
        description: Evento não encontrado
        content:
          application/json:
            example:
              error: "Evento não encontrado"
      400:
        description: Erro ao atualizar status do evento
        content:
          application/json:
            example:
              error: "Erro ao atualizar status do evento"
              details: "Detalhes do erro"
    """
    estado_atual = request.form.get('estadoAtualAgenda')
    
    if not estado_atual:
        return jsonify({"error": "Estado atual da agenda é obrigatório"}), 400
    
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE eventos SET estadoAtualAgenda = ? WHERE id = ?", (estado_atual, evento_id))
            if cursor.rowcount == 0:
                return jsonify({"error": "Evento não encontrado"}), 404
            
            # Buscar o evento atualizado para incluir na resposta
            cursor.execute("SELECT id, estadoAtualAgenda FROM eventos WHERE id = ?", (evento_id,))
            evento = cursor.fetchone()
            conn.commit()
        
        # Resposta com corpo separado
        return jsonify({
            "message": "Status do Evento atualizado com sucesso!"
        }), 200, {
            "evento": {
                "id": evento[0],
                "estadoAtualAgenda": evento[1]
            }
        }
    except sqlite3.Error as e:
        return jsonify({"error": "Erro ao atualizar status do evento", "details": str(e)}), 400


# Criar a tabela de eventos no banco de dados
if __name__ == '__main__':
    create_table()

# Iniciar a aplicação    
    app.run(host='0.0.0.0', port=5001, debug=True)

# FimS
