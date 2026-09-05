@echo off
chcp 65001 >nul
title Razum Google AI PRO - Sovereign Genome Orchestrator

echo ===================================================================
echo    RAZUM GOOGLE AI PRO • СУВЕРЕННАЯ АРХИТЕКТУРА «ГЕНОМ» (v4.0)
echo    Zero Trust • CardService • Video Synthesizer • NotebookLM Grounding
echo ===================================================================
echo.
echo Выберите режим работы:
echo [1] Запустить полный сквозной цикл (B2B карточка + 9:16 видео + NotebookLM)
echo [2] Запустить шлюз API / FastAPI сервер (порт 8000)
echo [3] Запустить автономный ночной харвестер (Overnight Harvester)
echo [4] Запустить полную диагностику тестов (41 тест pytest)
echo [5] Выход
echo.

set /p choice="Введите номер (1-5) [по умолчанию 1]: "
if "%choice%"=="" set choice=1

if "%choice%"=="1" goto full_cycle
if "%choice%"=="2" goto server_mode
if "%choice%"=="3" goto harvester_mode
if "%choice%"=="4" goto test_mode
if "%choice%"=="5" goto exit_app

:full_cycle
echo.
echo ===================================================================
echo Запуск сквозного пайплайна генерации...
echo ===================================================================
python main_orchestrator.py --mode full_cycle
echo.
echo Готово! Результаты сохранены в:
echo - Видео: output\rendered_videos\
echo - База знаний: 04_SALES_PLAYBOOK\ и 01_STRATEGY\
pause
exit /b 0

:server_mode
echo.
echo ===================================================================
echo Запуск локального API шлюза (FastAPI на http://127.0.0.1:8000)...
echo Для остановки нажмите Ctrl+C
echo ===================================================================
python main_orchestrator.py --mode server
pause
exit /b 0

:harvester_mode
echo.
echo ===================================================================
echo Запуск автономного ночного харвестера...
echo ===================================================================
python overnight_harvester.py
pause
exit /b 0

:test_mode
echo.
echo ===================================================================
echo Запуск полного набора архитектурных тестов...
echo ===================================================================
pytest tests/ -v
pause
exit /b 0

:exit_app
exit /b 0
