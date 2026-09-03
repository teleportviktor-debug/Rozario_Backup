# INSTALL.md — Руководство по установке
# Intelligence Module v2026.4

## Системные требования
- Windows 10/11 (x64) или Linux/macOS
- Python 3.10+
- Доступ к интернету для работы с Google Drive API

## Установка (5 шагов)

### Шаг 1: Распакуйте архив
Распакуйте `DELIVERY_PACKAGE.zip` в любую удобную папку.

### Шаг 2: Установите зависимости
Дважды кликните на `INSTALL_DEPENDENCIES.bat`
*(или в терминале: `pip install -r requirements.txt`)*

### Шаг 3: Добавьте ключ Google Drive
1. Откройте [Google Cloud Console](https://console.cloud.google.com)
2. IAM → Service Accounts → Ваш аккаунт → Keys → Add Key → JSON
3. Сохраните файл как `service_account.json` в папку проекта

### Шаг 4: Настройте переменные окружения
Откройте `.env.example`, переименуйте в `.env`, заполните:
```
GCP_SERVICE_ACCOUNT_JSON=<содержимое service_account.json>
DRIVE_INBOX_FOLDER=01_INBOX
```

### Шаг 5: Запуск
Дважды кликните на `QUICK_START.bat`

## Проверка установки
После запуска откройте Google Drive — должны появиться папки:
- `01_INBOX` — сюда загружайте файлы для конвертации
- `02_FOR_NOTEBOOK` — здесь появятся конвертированные Markdown-файлы
- `_ARCHIVE` — обработанные исходные файлы
