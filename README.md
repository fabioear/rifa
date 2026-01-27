# Sistema de Rifas

Sistema completo de gestão de rifas com Backend (FastAPI) e Frontend (React/Vite).

## Estrutura
- **Backend**: Python / FastAPI / SQLAlchemy / PostgreSQL
- **Frontend**: React / Vite / TailwindCSS
- **Banco de Dados**: PostgreSQL (Externo ou Docker)

## Como Rodar Localmente (Desenvolvimento)

1. **Backend**:
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Como Rodar no Servidor (Produção com Docker)

### Pré-requisitos
- Docker e Docker Compose instalados no servidor.
- Banco de Dados PostgreSQL já criado.

### Passo a Passo
1. **Clone o repositório**:
   ```bash
   git clone https://github.com/fabioear/rifa.git
   cd rifa
   ```

2. **Configure o ambiente**:
   ```bash
   cp .env.example .env
   nano .env
   ```
   *Ajuste a `DATABASE_URL` e credenciais do Twilio.*

3. **Execute o Deploy**:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```
   
   Ou manualmente:
   ```bash
   docker-compose up -d --build
   ```

### Portas
- **Backend API**: 8800 (Ex: http://seu-ip:8800)
- **Frontend**: 8801 (Ex: http://seu-ip:8801)

### Nginx (Proxy Reverso)
Use o arquivo `nginx_proxy_example.conf` como base para configurar seu domínio (ex: rifas.seudominio.com).
