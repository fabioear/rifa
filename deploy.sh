#!/bin/bash

# Script de Deploy Simplificado
echo "========================================"
echo "Iniciando Deploy - Sistema de Rifas"
echo "========================================"

# 1. Atualizar repositório
echo "[1/4] Baixando atualizações do Git..."
git pull origin main

# 2. Verificar .env
if [ ! -f .env ]; then
    echo "[!] Arquivo .env não encontrado!"
    echo "    Criando a partir de .env.example..."
    cp .env.example .env
    echo "    ⚠️  IMPORTANTE: Edite o arquivo .env com as senhas de produção antes de continuar."
    exit 1
fi

# 3. Limpeza Preventiva (Opcional mas recomendada se houver conflito)
echo "[2/4] Verificando conflitos..."
# Se existirem containers antigos rodando nas portas 8800/8801, avisa ou para.
# Aqui apenas garantimos que o docker-compose atual seja respeitado.

# 4. Subir containers
echo "[3/4] Construindo e subindo containers..."
docker-compose up -d --build --remove-orphans

# 5. Verificação de Saúde
echo "[4/4] Verificando status..."
sleep 5
docker-compose ps

echo "========================================"
echo "Deploy Concluído!"
echo "Backend: http://localhost:8800"
echo "Frontend: http://localhost:8801"
echo "Se o frontend estiver reiniciando, verifique os logs: docker logs frontend_rifas"
echo "========================================"
