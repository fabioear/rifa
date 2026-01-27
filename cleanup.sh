#!/bin/bash

echo "========================================"
echo "Limpeza de Containers Antigos"
echo "========================================"

# Lista de containers antigos para remover
OLD_CONTAINERS="rifa-backend rifa-frontend rifa-db"

for container in $OLD_CONTAINERS; do
    if docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
        echo "Parando e removendo: $container"
        docker stop $container
        docker rm $container
    else
        echo "Container $container não encontrado (já removido ou nome diferente)."
    fi
done

echo "========================================"
echo "Limpeza Concluída!"
echo "Agora você pode rodar ./deploy.sh sem conflitos."
echo "========================================"
