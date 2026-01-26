# Deploy no Servidor Remoto (177.131.169.119)

Para implantar o sistema no servidor onde já existe outro sistema rodando ("imperiojb"), siga estes passos:

1.  **Copie os arquivos para o servidor**:
    Como já existe uma estrutura em `/var/www/`, vamos criar uma pasta dedicada para o novo sistema.
    
    Exemplo via SCP (rodar da sua máquina local Windows):
    ```powershell
    # Exemplo copiando tudo da pasta atual para a pasta /var/www/rifa no servidor
    scp -r . root@191.252.218.33:/var/www/rifa
    ```

2.  **Acesse o servidor via SSH**:
    ```bash
    ssh root@191.252.218.33
    
    # Crie a pasta se ainda não existir (caso o scp não crie)
    mkdir -p /var/www/rifa
    
    # Entre na pasta
    cd /var/www/rifa
    ```

3.  **Verifique o arquivo .env**:
    Certifique-se de que o arquivo `.env` foi copiado e contém a variável `VITE_API_URL` apontando para o IP do servidor:
    `VITE_API_URL=http://191.252.218.33:8010/api/v1`

4.  **Suba os containers**:
    ```bash
    docker-compose up -d --build
    ```

5.  **Acesse o sistema**:
    - Frontend: http://177.131.169.119:8090
    - Backend: http://177.131.169.119:8010/docs

## Portas Configuradas
Para evitar conflito com o sistema existente, configuramos as seguintes portas externas:
- **Frontend**: 8090
- **Backend**: 8010
- **Banco de Dados**: 5433
