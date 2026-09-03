@echo off
chcp 65001 >nul
title Razum AI - Установка зависимостей (Python 3.14)

set "PYTHON_EXE=python"
if exist "C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe" (
    set "PYTHON_EXE=C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe"
)

echo ===================================================================
echo   Установка библиотек через: %PYTHON_EXE%
echo ===================================================================
echo.

"%PYTHON_EXE%" -m pip install --upgrade pip
"%PYTHON_EXE%" -m pip install -r requirements.txt

echo.
echo ===================================================================
echo   [V] Все зависимости успешно установлены!
echo ===================================================================
pause
