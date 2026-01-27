#!/bin/bash

# Script de Deploy Simplificado
echo "========================================"
echo "Iniciando Deploy - Sistema de Rifas"
echo "========================================"

# 1. Atualizar repositório
echo "[1/3] Baixando atualizações do Git..."
git pull origin main

# 2. Verificar .env
if [ ! -f .env ]; then
    echo "[!] Arquivo .env não encontrado!"
    echo "    Criando a partir de .env.example..."
    cp .env.example .env
    echo "    ⚠️  IMPORTANTE: Edite o arquivo .env com as senhas de produção antes de continuar."
    echo "    Use: nano .env"
    exit 1
fi

# 3. Subir containers
echo "[2/3] Construindo e subindo containers..."
docker-compose up -d --build

# 4. Limpar imagens antigas (opcional, para economizar espaço)
echo "[3/3] Limpando imagens não utilizadas..."
docker image prune -f

echo "========================================"
echo "Deploy Concluído com Sucesso!"
echo "Backend: http://localhost:8800"
echo "Frontend: http://localhost:8801"
echo "========================================"
