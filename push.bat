@echo off
setlocal enabledelayedexpansion

REM Carregar configuracoes
call "%~dp0config.bat"

echo ========================================
echo Git Push & Deploy - Rifa System
echo ========================================
echo Server: %HOST%
echo ========================================
echo.

REM Verificar chave SSH
if not exist "%KEY%" (
    echo [ERRO] Chave SSH nao encontrada: %KEY%
    echo Verifique se o arquivo "key" existe na raiz do projeto.
    pause
    exit /b 1
)

REM 1. Git Init e Commit (se necessario)
if not exist ".git" (
    echo [GIT] Inicializando repositorio...
    git init
    git branch -M main
)

echo [GIT] Adicionando arquivos...
git add .
git commit -m "Auto-deploy: %date% %time%"

REM 2. Configurar Remote do Servidor (Git Bare Repo)
echo [DEPLOY] Configurando remote do servidor...
git remote remove server 2>nul
git remote add server %USER%@%HOST%:/var/www/rifa.git

REM 3. Preparar Servidor (Criar pastas e Git Bare)
echo [DEPLOY] Preparando servidor...
ssh -o StrictHostKeyChecking=no -i "%KEY%" %USER%@%HOST% "mkdir -p /var/www/rifa.git && cd /var/www/rifa.git && git init --bare && mkdir -p /var/www/rifa"

REM 4. Enviar Codigo (Git Push)
echo [DEPLOY] Enviando codigo para o servidor...
set "GIT_SSH_COMMAND=ssh -i "%KEY%" -o StrictHostKeyChecking=no"
git push server main

REM 5. Checkout no Servidor (Deploy)
echo [DEPLOY] Atualizando arquivos no servidor...
ssh -o StrictHostKeyChecking=no -i "%KEY%" %USER%@%HOST% "git --work-tree=/var/www/rifa --git-dir=/var/www/rifa.git checkout -f"

REM 6. Enviar .env
echo [DEPLOY] Enviando arquivo .env...
scp -o StrictHostKeyChecking=no -i "%KEY%" .env %USER%@%HOST%:/var/www/rifa/.env

REM 7. Subir Docker
echo [DOCKER] Reiniciando servicos...
ssh -o StrictHostKeyChecking=no -i "%KEY%" %USER%@%HOST% "cd /var/www/rifa && docker compose down && docker compose up -d --build"

echo.
echo ========================================
echo [SUCESSO] Deploy concluido!
echo Frontend: http://%HOST%:8090
echo Backend:  http://%HOST%:8010
echo ========================================
pause
