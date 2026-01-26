# Sistema de Rifas Multi-Tenant

Este projeto contém o código fonte do sistema de rifas, composto por um backend em FastAPI e um frontend em React.

## Estrutura

- `backend/`: API RESTful com FastAPI, SQLAlchemy e PostgreSQL.
- `frontend/`: Single Page Application (SPA) com React, Vite e Tailwind CSS.

## Pré-requisitos

- Docker
- Docker Compose

## Como Rodar

1.  **Clone o repositório** (se ainda não o fez).

2.  **Verifique as variáveis de ambiente**:
    O arquivo `.env` na raiz já contém configurações padrão para desenvolvimento local.
    Se necessário, ajuste valores como senhas ou chaves secretas.

3.  **Suba os containers**:
    Execute o comando na raiz do projeto:

    ```bash
    docker-compose up -d --build
    ```

    Isso irá:
    - Criar o container do banco de dados PostgreSQL.
    - Criar e iniciar o container do Backend (que rodará as migrations e criará o usuário admin automaticamente).
    - Criar e iniciar o container do Frontend.

4.  **Acesse a aplicação** (no servidor remoto):

    - **Frontend**: `http://177.131.169.119:8090`
    - **Backend (Docs)**: `http://177.131.169.119:8010/docs`

    *Nota: As portas foram alteradas para evitar conflito com outros sistemas no servidor.*

## Credenciais Iniciais

O sistema cria automaticamente um usuário administrador global na primeira execução:

- **Email**: `admin@example.com`
- **Senha**: `admin`

## Migrations

As migrations do banco de dados são executadas automaticamente na inicialização do container `backend`.
Caso precise rodar migrations manualmente ou criar novas:

1.  Entre no container do backend:
    ```bash
    docker-compose exec backend bash
    ```

2.  Rode os comandos do Alembic:
    ```bash
    alembic revision --autogenerate -m "mensagem"
    alembic upgrade head
    ```

## Volumes

Os dados do banco de dados são persistidos no volume Docker `postgres_data`. Para resetar o banco completamente:

```bash
docker-compose down -v
```
