#!/bin/bash

# Script para corrigir a conexão com o banco de dados no .env

echo "========================================"
echo "Corrigindo conexão com Banco de Dados..."
echo "========================================"

if [ ! -f .env ]; then
    echo "Erro: Arquivo .env não encontrado."
    exit 1
fi

# Backup
cp .env .env.bak
echo "Backup criado em .env.bak"

# Substituir DATABASE_URL para usar o container 'db'
# Procura qualquer linha começando com DATABASE_URL= e substitui
sed -i 's|^DATABASE_URL=.*|DATABASE_URL=postgresql://postgres:postgres@db:5432/app_db|' .env

echo "Arquivo .env atualizado:"
grep "DATABASE_URL" .env

echo "========================================"
echo "Reiniciando containers..."
docker-compose down
docker-compose up -d --build --remove-orphans

echo "Aguardando inicialização..."
sleep 10
docker-compose ps

echo "========================================"
echo "Concluído! Tente acessar novamente."
