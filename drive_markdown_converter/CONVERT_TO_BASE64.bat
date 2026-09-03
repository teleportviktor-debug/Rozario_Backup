@echo off
chcp 65001 >nul
title Razum AI - Конвертер service_account.json в Base64

set "PYTHON_EXE=python"
if exist "C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe" (
    set "PYTHON_EXE=C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe"
)

if not exist service_account.json (
    echo [!] Файл service_account.json не найден в этой папке.
    echo Положите скачанный ключ service_account.json в эту папку и запустите снова.
    echo.
    pause
    exit /b
)

powershell -Command "[Convert]::ToBase64String([System.IO.File]::ReadAllBytes('service_account.json')) | Set-Clipboard; [Convert]::ToBase64String([System.IO.File]::ReadAllBytes('service_account.json')) | Out-File -Encoding ascii base64_key.txt"

echo ===================================================================
echo   [V] УСПЕШНО! Base64-строка скопирована в буфер обмена!
echo   [V] Также она сохранена в файл: base64_key.txt
echo ===================================================================
echo.
echo Теперь просто откройте Railway / переменные окружения и нажмите Ctrl+V.
echo.
pause
