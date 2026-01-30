@echo off
echo Iniciando Tunel SSH para Banco de Dados...
echo Isso permitira que seu backend local conecte ao banco seguro no VPS.
echo.
echo Mantenha essa janela ABERTA enquanto usar o sistema localmente.
echo.
ssh -i key -N -L 5433:127.0.0.1:5432 root@191.252.218.33
pause
