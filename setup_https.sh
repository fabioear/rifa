#!/bin/bash

DOMAIN="imperiodasrifas.app.br"
EMAIL="admin@imperiodasrifas.app.br"

echo "========================================"
echo "Configurando HTTPS para $DOMAIN..."
echo "========================================"

# Verificar se é root
if [ "$EUID" -ne 0 ]; then 
  echo "Por favor, execute como root"
  exit 1
fi

# 1. Instalar Certbot e Plugin Nginx (se necessário)
if ! command -v certbot &> /dev/null; then
    echo "Instalando Certbot..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
fi

# 2. Criar configuração Nginx Base (Porta 80)
echo "Criando arquivo de configuração do Nginx..."
cat > /etc/nginx/sites-available/$DOMAIN <<EOF
server {
    server_name $DOMAIN;

    # Frontend (React)
    location / {
        proxy_pass http://localhost:8801;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }

    # Backend (API)
    location /api {
        proxy_pass http://localhost:8800;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Docs
    location /docs {
        proxy_pass http://localhost:8800;
        proxy_set_header Host \$host;
    }
    
    location /openapi.json {
        proxy_pass http://localhost:8800;
        proxy_set_header Host \$host;
    }
}
EOF

# 3. Habilitar site
echo "Habilitando site..."
ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/

# 4. Testar e Recarregar Nginx
echo "Testando configuração Nginx..."
nginx -t

if [ $? -eq 0 ]; then
    echo "Configuração OK. Recarregando Nginx..."
    systemctl reload nginx
else
    echo "Erro na configuração do Nginx. Abortando."
    exit 1
fi

# 5. Executar Certbot
echo "Executando Certbot para gerar certificado SSL..."
# --nginx: usa o plugin nginx
# --non-interactive: não pergunta nada
# --agree-tos: aceita os termos
# --redirect: força redirecionamento HTTP -> HTTPS
certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $EMAIL --redirect

echo "========================================"
echo "HTTPS configurado com sucesso!"
echo "Acesse: https://$DOMAIN"
