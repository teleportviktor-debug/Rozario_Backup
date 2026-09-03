@echo off
chcp 65001 >nul
title Razum AI - 1-Click Railway Deploy Helper

set "PYTHON_EXE=python"
if exist "C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe" (
    set "PYTHON_EXE=C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe"
)

"%PYTHON_EXE%" prepare_railway.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [Резервное копирование через PowerShell...]
    if exist service_account.json (
        powershell -Command "Get-Content service_account.json -Raw | Set-Clipboard"
        echo.
        echo ===================================================================
        echo   [V] ВСЁ ГОТОВО! JSON СКОПИРОВАН В БУФЕР ОБМЕНА!
        echo ===================================================================
        echo.
        echo Откройте Railway -> Variables -> Добавьте переменную:
        echo   Имя:      GCP_SERVICE_ACCOUNT_JSON
        echo   Значение: Нажмите Ctrl+V
        echo.
    ) else (
        echo [X] Файл service_account.json не найден в этой папке!
    )
    pause
)
