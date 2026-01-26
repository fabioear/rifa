@echo off
setlocal enabledelayedexpansion

REM Carregar configuracoes
call "%~dp0config.bat"

echo ========================================
echo Git Push & Deploy - Rifa System
echo ========================================
echo.

REM 1. Git Push
echo [GIT] Adicionando arquivos...
git add .
echo.

echo [GIT] Fazendo commit...
git commit -m "Update via push.bat"
echo.

echo [GIT] Enviando para o GitHub...
git push -u origin main
echo.

REM 3. Deploy no Servidor
echo ========================================
echo [DEPLOY] Iniciando deploy em %HOST%...
echo ========================================

REM Criar pasta remota
echo [1/3] Criando pasta remota %REMOTE_DIR%...
ssh -o IdentitiesOnly=yes -i "%KEY%" %USER%@%HOST% "mkdir -p %REMOTE_DIR%"

REM Copiar arquivos (Usando Git + SCP para configs)
echo [2/3] Atualizando arquivos no servidor...

REM Envia apenas o .env e docker-compose.yml via SCP (rapido)
scp -o IdentitiesOnly=yes -i "%KEY%" .env %USER%@%HOST%:%REMOTE_DIR%/.env
scp -o IdentitiesOnly=yes -i "%KEY%" docker-compose.yml %USER%@%HOST%:%REMOTE_DIR%/docker-compose.yml

REM Atualiza codigo via Git no servidor (muito mais rapido que SCP)
ssh -o IdentitiesOnly=yes -i "%KEY%" %USER%@%HOST% "if [ ! -d %REMOTE_DIR%/.git ]; then git clone https://github.com/fabioear/rifa.git %REMOTE_DIR%; else cd %REMOTE_DIR% && git pull origin main; fi"

REM Executar Docker Compose
echo [3/3] Atualizando containers no servidor...
ssh -o IdentitiesOnly=yes -i "%KEY%" %USER%@%HOST% "cd %REMOTE_DIR% && docker-compose up -d --build"

echo.
echo ========================================
echo Deploy Concluido!
echo ========================================
pause
endlocal
