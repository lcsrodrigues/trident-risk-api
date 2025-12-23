# Trident Energy Risk Manager API

API REST em Python (FastAPI) para consulta do sistema de gestão de riscos da Trident Energy.

## Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **MySQL** - Banco de dados
- **Pydantic** - Validação de dados
- **Uvicorn** - Servidor ASGI

## Endpoints Disponíveis

### Root
- `GET /` - Health check da API
- `GET /health` - Status de saúde para Render
- `GET /docs` - Documentação Swagger UI
- `GET /redoc` - Documentação ReDoc

### Usuários
- `GET /api/users` - Lista todos os usuários
- `GET /api/users/{id}` - Busca usuário por ID
- `GET /api/users/count` - Contagem de usuários por role

### Roles
- `GET /api/roles` - Lista todos os papéis

### Países
- `GET /api/countries` - Lista todos os países

### Riscos
- `GET /api/risks` - Lista todos os riscos
- `GET /api/risks/{id}` - Busca risco por ID (com controles, ações e comentários)
- `GET /api/risks/summary/by-country` - Resumo de riscos por país
- `GET /api/risks/summary/heatmap` - Dados para heatmap de riscos

### Planos de Ação
- `GET /api/action-plans` - Lista todos os planos de ação

### Dashboard
- `GET /api/dashboard/summary` - Estatísticas gerais do dashboard

## Deploy no Render

### Passo 1: Criar repositório no GitHub

```bash
# Clone ou crie um novo repositório
git init
git add .
git commit -m "Initial commit - Trident Risk Manager API"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/trident-risk-api.git
git push -u origin main
```

### Passo 2: Configurar no Render

1. Acesse [render.com](https://render.com) e faça login
2. Clique em **New +** > **Web Service**
3. Conecte seu repositório GitHub
4. Configure:
   - **Name**: `trident-risk-api`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Passo 3: Configurar Variáveis de Ambiente

No dashboard do Render, vá em **Environment** e adicione:

| Key | Value |
|-----|-------|
| `DB_HOST` | `sql7.freesqldatabase.com` |
| `DB_NAME` | `sql7812701` |
| `DB_USER` | `sql7812701` |
| `DB_PASSWORD` | `SUA_SENHA_DO_BANCO` |
| `DB_PORT` | `3306` |

### Passo 4: Deploy

O Render fará o deploy automaticamente após configurar. A URL será algo como:
```
https://trident-risk-api.onrender.com
```

## Desenvolvimento Local

### Instalar dependências

```bash
pip install -r requirements.txt
```

### Configurar variáveis de ambiente

Crie um arquivo `.env`:

```env
DB_HOST=sql7.freesqldatabase.com
DB_NAME=sql7812701
DB_USER=sql7812701
DB_PASSWORD=sua_senha
DB_PORT=3306
```

### Executar

```bash
uvicorn app.main:app --reload --port 8000
```

Acesse: http://localhost:8000/docs

## Estrutura do Projeto

```
trident_api/
├── app/
│   ├── __init__.py
│   ├── main.py          # Endpoints da API
│   ├── database.py      # Conexão com banco de dados
│   └── models.py        # Modelos Pydantic
├── requirements.txt     # Dependências Python
├── render.yaml          # Configuração do Render
├── .gitignore
└── README.md
```

## Exemplos de Uso

### Listar usuários
```bash
curl https://trident-risk-api.onrender.com/api/users
```

### Buscar riscos por país (Brasil = 2)
```bash
curl "https://trident-risk-api.onrender.com/api/risks?country_id=2"
```

### Dashboard summary
```bash
curl https://trident-risk-api.onrender.com/api/dashboard/summary
```

## Licença

Propriedade de Trident Energy.
