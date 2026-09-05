@echo off
chcp 65001 >nul
title Razum Google AI PRO - n8n Workflow Automation (Port 5678)
color 0B

echo ===================================================================
echo    RAZUM GOOGLE AI PRO • ЗАПУСК СЕРВЕРА N8N (ПОРТ 5678)
echo    Sovereign B2B Outreach & Google Sheets Integration Hub
echo ===================================================================
echo.

echo [1/3] Проверка активности порта 5678...
netstat -ano | findstr :5678 >nul
if %errorlevel% equ 0 (
    echo [INFO] Сервер n8n уже запущен на порту 5678.
    goto open_check
)

echo [2/3] Запуск сервиса n8n на http://localhost:5678 ...
start "n8n Studio (Port 5678)" python -m uvicorn services.integration.n8n_server:app --host 0.0.0.0 --port 5678

:open_check
echo [3/3] Ожидание готовности сервера...
timeout /t 2 /nobreak >nul

echo.
echo ===================================================================
echo n8n сервер АКТИВЕН!
echo Веб-интерфейс: http://localhost:5678
echo Проверка здоровья: http://localhost:5678/healthz
echo ===================================================================
echo.

start http://localhost:5678
exit /b 0
