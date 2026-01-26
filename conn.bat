@echo off
setlocal

call "%~dp0config.bat"

echo Conectando em %USER%@%HOST%...
ssh -o IdentitiesOnly=yes -i "%KEY%" %USER%@%HOST%

endlocal
