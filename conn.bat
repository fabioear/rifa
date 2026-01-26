@echo off
setlocal

REM Caminho da chave na raiz do projeto
set "KEY=%~dp0key"

REM Ajuste o usuário e o IP/host do servidor
set "USER=root"
set "HOST=191.252.218.33"

REM Conectar via SSH usando a chave especificada
ssh -o IdentitiesOnly=yes -i "%KEY%" %USER%@%HOST%

endlocal