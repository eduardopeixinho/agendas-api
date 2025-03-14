# Agendas API

Este projeto é uma API para gerenciamento dos eventos de uma Agenda, desenvolvida em **Python** utilizando **Flask**, documentação de API **Swagger**, banco de dados **SQLite** e empacotada com **Docker**.

## Como construir e rodar o contêiner

### Clonar o repositório
```sh
git clone https://github.com/eduardopeixinho/agendas-api.git
```
### Acessar diretório com os arquivos
```sh
cd agendas-api/artefatos/
```

### Construir a imagem Docker
Execute o seguinte comando para criar a imagem Docker a partir do `Dockerfile`:

```sh
docker build -t agenda-api:1.0 -f AgendaApi.Dockerfile .
```

### Rodar o contêiner
Após construir a imagem, execute o contêiner com:

```sh
docker run -d -p 5000:5000 --name agenda-api agenda-api:1.0
```

### Link para acesso
Utilizar o seguinte link para acessar a API:
```sh
http://127.0.0.1:5000/
```
---
### Estrutura do Banco de Dados

A API utiliza um banco de dados relacional SQLite com a seguinte estrutura para o gerenciamento dos eventos da agenda:

### Tabela: **eventos**
| Coluna     | Tipo        | Descrição                          |
|------------|-------------|------------------------------------|
| evento_id         | INTEGER     | Chave primária, auto-incremento    |
| titulo     | TEXT| Título da agenda                  |
| local     | TEXT| Título da agenda    
| descricao | TEXT        | Descrição da agenda               |
| dataInicio       | TEXT| Data e hora de início do evento (AAAA-MM-DD HH:MM)     |
| dataFim       | TEXT| Data e hora do fim do evento (AAAA-MM-DD HH:MM)            |
| estadoAtualAgenda       | TEXT| Situação do Evento (Valores possíveis: 'RECEBIDO', 'CONFIRMADO', 'ATENDIDO', 'CANCELADO')             |

---

### Rotas Disponíveis na API

A seguir estão as rotas disponíveis para interação com a **API de eventos da Agenda**.

### **1. Obter todos os eventos da agenda**
**GET** `/eventos`

**Descrição:** Retorna uma lista de todos os eventos da agenda.

### **2. Criar novo evento na agenda**
**POST** `/eventos`

**Descrição:** Cria um novo evento na agenda.
```json
{
  "dataFim": "string",
  "dataInicio": "string",
  "descricao": "string",
  "estadoAtualAgenda": "string",
  "local": "string",
  "titulo": "string"
}
```
### **3. Obter evento específico**
**GET** `/eventos/{id}`

**Descrição:** Retorna os detalhes de um evento específico.

### **4. Atualizar evento da agenda**
**PUT** `/eventos/{id}`

**Descrição:** Atualiza os dados de um evento existente.

### **5. Atualizar status do evento da agenda**
**PUT** `/eventos/status/{id}`

**Descrição:** Atualiza o status de um evento existente.

### **6. Excluir evento da agenda**
**DELETE** `/evento/{id}`

**Descrição:** Exclui um evento da agenda.


