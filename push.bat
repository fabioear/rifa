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

REM Copiar arquivos (Usando SCP)
echo [2/3] Copiando arquivos para o servidor...
REM Copia arquivos essenciais e pastas. 
REM Nota: SCP recursivo pode ser lento se tiver node_modules. 
REM O ideal seria usar rsync ou git pull no servidor, mas vamos garantir o envio dos configs.

scp -o IdentitiesOnly=yes -i "%KEY%" .env %USER%@%HOST%:%REMOTE_DIR%/.env
scp -o IdentitiesOnly=yes -i "%KEY%" docker-compose.yml %USER%@%HOST%:%REMOTE_DIR%/docker-compose.yml
scp -o IdentitiesOnly=yes -i "%KEY%" -r backend %USER%@%HOST%:%REMOTE_DIR%/
scp -o IdentitiesOnly=yes -i "%KEY%" -r frontend %USER%@%HOST%:%REMOTE_DIR%/

REM Executar Docker Compose
echo [3/3] Atualizando containers no servidor...
ssh -o IdentitiesOnly=yes -i "%KEY%" %USER%@%HOST% "cd %REMOTE_DIR% && docker-compose up -d --build"

echo.
echo ========================================
echo Deploy Concluido!
echo ========================================
pause
endlocal
