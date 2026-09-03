@echo off
chcp 65001 > nul
title Zero API Workspace Engine — Daily Sync

echo ===================================================================
echo   DAILY SYNC — Zero API Workspace Engine
echo   Синхронизация памяти агентов на Google Drive + Git (если настроен)
echo ===================================================================
echo.

set PYTHON=C:\Users\user\AppData\Local\Programs\Python\Python314\python.exe
set PROJECT=c:\Users\user\ГУГЛ ИМПЕРИЯ

cd /d "%PROJECT%"

REM 1. Sync на Google Drive
echo [1/2] Синхронизирую _MEMORY/ и рабочие папки на Google Drive...
"%PYTHON%" tools\memory_sync.py
echo.

REM 2. Git push (если git установлен и remote настроен)
echo [2/2] Попытка git push...
where git >nul 2>&1
if %errorlevel%==0 (
    "%PYTHON%" tools\memory_sync.py --git --message "memory: daily sync от %date% %time%"
) else (
    echo [INFO] Git не установлен — пропускаю git push.
    echo        Скачать git: https://git-scm.com/download/win
)

echo.
echo ===================================================================
echo   [OK] Синхронизация завершена!
echo   Файлы обновлены на Google Drive: G:\Мой диск\AI_WORK_SYSTEM\
echo ===================================================================
echo.
pause
