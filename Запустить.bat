@echo off
chcp 65001 >nul
echo ========================================
echo   Flower CRM - Запуск сервера
echo ========================================
echo.
echo Запуск сервера...
echo.
cd /d "%~dp0"
start http://127.0.0.1:5000
python app.py
pause
