@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONPATH=%~dp0
title Razum Outreach Pipeline

echo ===================================================================
echo    RAZUM OUTREACH PIPELINE - FULL AUTONOMOUS 1-CLICK LAUNCH
echo ===================================================================
echo.
echo [1/2] Запуск фонового воркера Google Sheets...
start "Sheets Worker" python -m services.integration.sheets_worker

echo [2/2] Запуск FastAPI сервера (Port 8000)...
python -m uvicorn services.integration.n8n_bridge:app --host 0.0.0.0 --port 8000
