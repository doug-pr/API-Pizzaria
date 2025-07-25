# 🍕 Sistema de Pedidos de Pizzaria - FastAPI

Um sistema completo de gerenciamento de pedidos de pizzaria desenvolvido com FastAPI, incluindo autenticação JWT, gerenciamento de usuários e controle de pedidos.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Executando o Projeto](#executando-o-projeto)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [API Endpoints](#api-endpoints)
- [Banco de Dados](#banco-de-dados)
- [Autenticação](#autenticação)
- [Contribuição](#contribuição)

## 🎯 Sobre o Projeto

Este é um sistema de pedidos de pizzaria desenvolvido com FastAPI que permite:
- Cadastro e autenticação de usuários
- Criação e gerenciamento de pedidos
- Adição e remoção de itens nos pedidos
- Controle de status dos pedidos (PENDENTE, CANCELADO, FINALIZADO)
- Sistema de permissões (usuários comuns e administradores)

## ✨ Funcionalidades

### 🔐 Autenticação
- Cadastro de novos usuários
- Login com JWT tokens
- Refresh tokens para renovação automática
- Sistema de permissões (usuário/admin)

### 📦 Gerenciamento de Pedidos
- Criação de novos pedidos
- Adição de itens (pizzas) aos pedidos
- Cálculo automático do preço total
- Cancelamento de pedidos
- Finalização de pedidos
- Listagem de pedidos por usuário
- Visualização detalhada de pedidos

### 👥 Controle de Usuários
- Cadastro com validação de email único
- Senhas criptografadas com bcrypt
- Controle de usuários ativos/inativos
- Diferenciação entre usuários comuns e administradores

## 🛠 Tecnologias Utilizadas

- **FastAPI** - Framework web moderno e rápido para Python
- **SQLAlchemy** - ORM para Python
- **Alembic** - Ferramenta de migração de banco de dados
- **SQLite** - Banco de dados relacional
- **Pydantic** - Validação de dados usando Python type hints
- **JWT (Jose)** - Autenticação baseada em tokens
- **Passlib + Bcrypt** - Criptografia de senhas
- **Python-dotenv** - Gerenciamento de variáveis de ambiente
- **Uvicorn** - Servidor ASGI para FastAPI

## 📋 Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## 🚀 Instalação

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd fastapi-pedidos-pizzaria
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
```

3. **Ative o ambiente virtual**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Instale as dependências**
```bash
pip install -r requirements.txt
```

## ⚙️ Configuração

1. **Configure as variáveis de ambiente**
   
   O arquivo `.env` já está configurado com valores padrão:
   ```env
   SECRET_KEY="SUA KEY"
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

2. **Execute as migrações do banco de dados**
```bash
alembic upgrade head
```

## 🏃‍♂️ Executando o Projeto

1. **Inicie o servidor de desenvolvimento**
```bash
uvicorn main:app --reload
```

2. **Acesse a aplicação**
   - API: http://localhost:8000
   - Documentação interativa (Swagger): http://localhost:8000/docs
   - Documentação alternativa (ReDoc): http://localhost:8000/redoc

## 📁 Estrutura do Projeto

```
├── main.py                 # Arquivo principal da aplicação
├── models.py              # Modelos do banco de dados (SQLAlchemy)
├── schemas.py             # Schemas de validação (Pydantic)
├── auth_routes.py         # Rotas de autenticação
├── order_routes.py        # Rotas de pedidos
├── dependencies.py        # Dependências compartilhadas
├── requirements.txt       # Dependências do projeto
├── .env                   # Variáveis de ambiente
├── .gitignore            # Arquivos ignorados pelo Git
├── alembic.ini           # Configuração do Alembic
└── testes.py             # Arquivo de testes
```

## 🔌 API Endpoints

### 🔐 Autenticação (`/auth`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/auth/` | Rota padrão de autenticação |
| POST | `/auth/criar-conta` | Cadastrar novo usuário |
| POST | `/auth/login` | Login com email/senha |
| POST | `/auth/login-form` | Login via formulário OAuth2 |
| GET | `/auth/refresh` | Renovar token de acesso |

### 📦 Pedidos (`/pedidos`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/pedidos/` | Rota padrão de pedidos |
| POST | `/pedidos/criar-pedido` | Criar novo pedido |
| POST | `/pedidos/cancelar/{id_pedido}` | Cancelar pedido |
| GET | `/pedidos/listar` | Listar todos os pedidos (admin) |
| POST | `/pedidos/adicionar-item/{id_pedido}` | Adicionar item ao pedido |
| POST | `/pedidos/remover-item/{id_item_pedido}` | Remover item do pedido |
| POST | `/pedidos/finalizar/{id_pedido}` | Finalizar pedido |
| GET | `/pedidos/pedido/{id_pedido}` | Visualizar pedido específico |
| GET | `/pedidos/pedidos-usuario` | Listar pedidos do usuário logado |

## 🗄️ Banco de Dados

O sistema utiliza SQLite com as seguintes tabelas:

### Usuários (`usuarios`)
- `id` (Integer, PK, Auto-increment)
- `nome` (String)
- `email` (String, Unique, Not Null)
- `senha` (String, Encrypted)
- `ativo` (Boolean, Default: True)
- `admin` (Boolean, Default: False)

### Pedidos (`pedidos`)
- `id` (Integer, PK, Auto-increment)
- `status` (String: PENDENTE/CANCELADO/FINALIZADO)
- `usuario` (Integer, FK para usuarios.id)
- `preco` (Float, calculado automaticamente)

### Itens do Pedido (`itens_pedido`)
- `id` (Integer, PK, Auto-increment)
- `quantidade` (Integer)
- `sabor` (String)
- `tamanho` (String)
- `preco_unitario` (Float)
- `pedido` (Integer, FK para pedidos.id)

## 🔒 Autenticação

O sistema utiliza JWT (JSON Web Tokens) para autenticação:

- **Access Token**: Válido por 30 minutos
- **Refresh Token**: Válido por 7 dias
- **Algoritmo**: HS256
- **Proteção**: Todas as rotas de pedidos requerem autenticação

### Permissões

- **Usuários Comuns**: Podem gerenciar apenas seus próprios pedidos
- **Administradores**: Podem visualizar e gerenciar todos os pedidos

## 🔧 Comandos Úteis

### Migrações do Banco de Dados
```bash
# Criar nova migração
alembic revision --autogenerate -m "Descrição da migração"

# Executar migrações
alembic upgrade head

# Reverter migração
alembic downgrade -1
```

### Desenvolvimento
```bash
# Executar servidor com reload automático
uvicorn main:app --reload

# Executar em porta específica
uvicorn main:app --reload --port 8080

# Executar com host específico
uvicorn main:app --reload --host 0.0.0.0
```

## 📝 Exemplos de Uso

### 1. Cadastrar Usuário
```bash
curl -X POST "http://localhost:8000/auth/criar-conta" \
     -H "Content-Type: application/json" \
     -d '{
       "nome": "João Silva",
       "email": "joao@email.com",
       "senha": "minhasenha123",
       "ativo": true,
       "admin": false
     }'
```

### 2. Fazer Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "joao@email.com",
       "senha": "minhasenha123"
     }'
```

### 3. Criar Pedido
```bash
curl -X POST "http://localhost:8000/pedidos/criar-pedido" \
     -H "Authorization: Bearer SEU_TOKEN_AQUI" \
     -H "Content-Type: application/json" \
     -d '{
       "usuario": 1
     }'
```

### 4. Adicionar Item ao Pedido
```bash
curl -X POST "http://localhost:8000/pedidos/adicionar-item/1" \
     -H "Authorization: Bearer SEU_TOKEN_AQUI" \
     -H "Content-Type: application/json" \
     -d '{
       "quantidade": 2,
       "sabor": "Margherita",
       "tamanho": "Grande",
       "preco_unitario": 35.90
     }'
```

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

Desenvolvido com ❤️ por Douglas Barcelos

---

⭐ Se este projeto te ajudou, considere dar uma estrela no repositório!
