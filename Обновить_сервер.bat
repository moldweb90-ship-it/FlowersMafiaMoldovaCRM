@echo off
chcp 65001 >nul
echo ========================================
echo   Flower CRM - Обновление сервера
echo ========================================
echo.
cd /d "%~dp0"
python update_server.py
echo.
echo Готово!
pause
