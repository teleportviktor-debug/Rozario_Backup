@echo off
chcp 65001 >nul
title Razum AI - Локальный запуск конвертера (Python 3.14)

set "PYTHON_EXE=python"
if exist "C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe" (
    set "PYTHON_EXE=C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe"
)

echo ===================================================================
echo   Запуск Google Drive to Markdown Converter
echo   Интерпретатор: %PYTHON_EXE%
echo ===================================================================
echo.
echo [1] Однократная обработка 01_INBOX (нажмите 1)
echo [2] Фоновый опрос 24/7 Daemon (нажмите 2)
echo.
set /p mode="Выберите режим (1 или 2): "

if "%mode%"=="2" (
    "%PYTHON_EXE%" main.py --daemon
) else (
    "%PYTHON_EXE%" main.py --once
)

echo.
pause
