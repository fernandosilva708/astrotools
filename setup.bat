@echo off
REM 
REM AstroTools - Criar estrutura de directórios e ficheiros vazios
REM Executar: setup.bat
REM 

set ROOT=C:\work\git\astrotools

mkdir "%ROOT%\app\auth"
mkdir "%ROOT%\app\gallery"
mkdir "%ROOT%\app\astrometry"
mkdir "%ROOT%\app\ephemeris"
mkdir "%ROOT%\app\telescopius"
mkdir "%ROOT%\app\backup"
mkdir "%ROOT%\app\dashboard"
mkdir "%ROOT%\app\static\css"
mkdir "%ROOT%\app\static\js"
mkdir "%ROOT%\app\static\img"
mkdir "%ROOT%\app\templates\auth"
mkdir "%ROOT%\app\templates\gallery"
mkdir "%ROOT%\app\templates\astrometry"
mkdir "%ROOT%\app\templates\ephemeris"
mkdir "%ROOT%\app\templates\telescopius"
mkdir "%ROOT%\app\templates\backup"
mkdir "%ROOT%\app\templates\dashboard"
mkdir "%ROOT%\migrations"
mkdir "%ROOT%\tests"

REM __init__.py vazios para cada módulo
type nul > "%ROOT%\app\auth\__init__.py"
type nul > "%ROOT%\app\gallery\__init__.py"
type nul > "%ROOT%\app\astrometry\__init__.py"
type nul > "%ROOT%\app\ephemeris\__init__.py"
type nul > "%ROOT%\app\telescopius\__init__.py"
type nul > "%ROOT%\app\backup\__init__.py"
type nul > "%ROOT%\app\dashboard\__init__.py"

echo.
echo Estrutura criada em %ROOT%
echo.
echo Agora copia os ficheiros gerados pelo Claude:
echo.
echo   app\__init__.py          ^<-- Factory Flask
echo   app\models.py            ^<-- Modelos SQLAlchemy
echo   app\auth\routes.py       ^<-- Autenticacao
echo   app\gallery\routes.py    ^<-- Galeria
echo   app\gallery\ingest.py    ^<-- Importacao Seestar
echo   app\astrometry\routes.py ^<-- Plate-solving
echo   app\ephemeris\routes.py  ^<-- Efemerides (renomear do artifact combinado)
echo   app\telescopius\routes.py^<-- Proxy Telescopius
echo   app\backup\routes.py     ^<-- Backup rclone
echo   app\dashboard\routes.py  ^<-- Dashboard
echo   app\templates\base.html
echo   app\templates\auth\login.html
echo   app\templates\dashboard\index.html
echo   run.py
echo   requirements.txt         ^<-- extrair do run.py
echo   .env                     ^<-- copiar de .env.example
echo.
pause
