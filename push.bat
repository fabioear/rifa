@echo off
echo ========================================
echo Git Push - Imperio JB
echo ========================================
echo.

REM Adicionar todas as alteracoes
echo [1/3] Adicionando alteracoes...
git add .
echo.

REM Fazer commit
echo [2/3] Fazendo commit...
git commit -m "commit automático"
echo.

REM Fazer push
echo [3/3] Enviando para o repositorio remoto...
git push origin main
echo.

echo ========================================
echo Concluido!
echo ========================================


