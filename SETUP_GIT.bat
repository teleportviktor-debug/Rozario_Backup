@echo off
chcp 65001 > nul
title Git Setup — Razum Google AI PRO

echo ===================================================================
echo   ПЕРВОНАЧАЛЬНАЯ НАСТРОЙКА GIT-РЕПОЗИТОРИЯ
echo   Repo: https://github.com/teleportviktor-debug/Rozario_Backup
echo ===================================================================
echo.

set PROJECT=c:\Users\user\ГУГЛ ИМПЕРИЯ
set GITHUB_URL=https://github.com/teleportviktor-debug/Rozario_Backup.git
set PYTHON=C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe
set GIT=C:\Program Files\Git\bin\git.exe

cd /d "%PROJECT%"

REM Проверяем что git установлен
if not exist "%GIT%" (
    echo [ERROR] Git не найден. Установите с: https://git-scm.com/download/win
    echo         После установки запустите этот файл снова.
    pause
    exit /b 1
)

echo [1/6] Настройка git user...
"%GIT%" config user.name "Razum AI Bot"
"%GIT%" config user.email "teleportviktor-debug@users.noreply.github.com"

echo [2/6] Инициализация репозитория...
"%GIT%" init
"%GIT%" branch -M main

echo [3/6] Подключение к GitHub...
"%GIT%" remote remove origin 2>nul
"%GIT%" remote add origin %GITHUB_URL%

echo [4/6] Добавление файлов (без секретов)...
"%GIT%" add .
REM Явно исключаем секреты на случай если .gitignore не сработал
"%GIT%" reset HEAD -- service_account.json 2>nul
"%GIT%" reset HEAD -- drive_markdown_converter\service_account.json 2>nul
"%GIT%" reset HEAD -- drive_markdown_converter\gen-lang-client-*.json 2>nul
"%GIT%" reset HEAD -- drive_markdown_converter\base64_key.txt 2>nul

echo [5/6] Первый коммит...
"%GIT%" commit -m "init: Zero API Workspace Engine v2.4.0 — Initial commit with _MEMORY system"

echo [6/6] Push на GitHub...
echo.
echo ВНИМАНИЕ: GitHub может запросить логин/пароль или Personal Access Token.
echo Если появится окно браузера — войдите в аккаунт teleportviktor-debug.
echo.
"%GIT%" push -u origin main

echo.
echo ===================================================================
echo   [OK] Репозиторий настроен!
echo   Ссылка: https://github.com/teleportviktor-debug/Rozario_Backup
echo ===================================================================
echo.
pause
