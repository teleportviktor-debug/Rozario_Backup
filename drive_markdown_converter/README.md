# 🚀 Google Drive to Markdown Converter (Zero-Friction Deploy)

Автономный микросервис для автоматического скачивания файлов из `01_INBOX` на Google Диске, конвертации в чистый Markdown через **Microsoft MarkItDown** / **IBM Docling** и выгрузки в `02_FOR_NOTEBOOK`.

---

## ⚡ ИНСТРУКЦИЯ ДЛЯ WINDOWS (1 КЛИК ДЛЯ RAILWAY)

Никаких консолей и ручного кодирования Base64. Только **Ctrl+C** и **Ctrl+V**:

### Шаг 1. Получите готовую строку в 1 клик
1. Положите скачанный файл `service_account.json` в папку `drive_markdown_converter`.
2. Дважды кликните по файлу:
   👉 **`ONE_CLICK_COPY_FOR_RAILWAY.bat`**
3. Скрипт сам прочитает файл и **автоматически скопирует готовую строку в ваш буфер обмена Windows**.

---

### Шаг 2. Вставьте в Railway
1. В панели [Railway.app](https://railway.app) перейдите в ваш проект -> вкладка **Variables**.
2. Добавьте переменную:
   * **Имя:** `GCP_SERVICE_ACCOUNT_JSON`
   * **Значение:** Нажмите **`Ctrl + V`** (вставится значение из буфера)
3. Нажмите кнопку **Add**. Всё! Микросервис развернут и сразу начинает работу 24/7.

---

## 📂 Файлы микросервиса

* 🎯 [ONE_CLICK_COPY_FOR_RAILWAY.bat](file:///c:/Users/user/ГУГЛ%20ИМПЕРИЯ/drive_markdown_converter/ONE_CLICK_COPY_FOR_RAILWAY.bat) — Запуск подготовки ключа в 1 клик на Windows.
* 📄 [main.py](file:///c:/Users/user/ГУГЛ%20ИМПЕРИЯ/drive_markdown_converter/main.py) — Главный пайплайн (CLI / 24/7 Daemon / Cloud Function).
* ⚙️ [drive_service.py](file:///c:/Users/user/ГУГЛ%20ИМПЕРИЯ/drive_markdown_converter/drive_service.py) — Google Drive API v3 клиент.
* 📑 [converter.py](file:///c:/Users/user/ГУГЛ%20ИМПЕРИЯ/drive_markdown_converter/converter.py) — Парсер MarkItDown / Docling / Fallback.
* 🔧 [config.py](file:///c:/Users/user/ГУГЛ%20ИМПЕРИЯ/drive_markdown_converter/config.py) — Конфиг с прямой поддержкой чистого JSON.
* 📦 [requirements.txt](file:///c:/Users/user/ГУГЛ%20ИМПЕРИЯ/drive_markdown_converter/requirements.txt) — Зависимости.
* 🐳 [Dockerfile](file:///c:/Users/user/ГУГЛ%20ИМПЕРИЯ/drive_markdown_converter/Dockerfile) — Докер-образ.
