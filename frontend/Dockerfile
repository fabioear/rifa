# Etapa 1: Build
FROM node:18-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Build da aplicação para produção
RUN npm run build

# Etapa 2: Servir com Nginx leve
FROM nginx:alpine

# Copiar os arquivos do build para o diretório do Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Configuração customizada do Nginx para SPA (Single Page Application)
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
