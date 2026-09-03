# Журнал ошибок и решений — Razum Google AI PRO

> **Правило:** Каждая ошибка фиксируется здесь. Агент 5 (Spark) проверяет этот файл перед запуском, чтобы не повторять ошибочные действия.

---

## ✅ RESOLVED: UnicodeEncodeError cp1251 в логах Windows
- **Дата:** 2026-09-01
- **Агент:** drive_markdown_converter/main.py
- **Симптом:** `UnicodeEncodeError: 'charmap' codec can't encode character '\u2713'` при выводе эмодзи в логах
- **Причина:** Windows консоль использует cp1251, Python logger не указывал encoding
- **Решение:** `sys.stdout.reconfigure(encoding='utf-8')` + убраны эмодзи из logger сообщений
- **Файлы изменены:** `drive_markdown_converter/main.py`, `drive_markdown_converter/drive_service.py`

---

## ✅ RESOLVED: ConnectionAbortedError WinError 10053 в daemon
- **Дата:** 2026-09-01 → 2026-09-02
- **Агент:** drive_markdown_converter/main.py (daemon loop)
- **Симптом:** Процесс падал через ~10 минут работы с `ConnectionAbortedError: [WinError 10053] Программа на вашем хост-компьютере разорвала установленное подключение`
- **Причина:** Windows разрывает длинные idle TCP-соединения с googleapis.com
- **Решение:** Добавлен exponential backoff (30→60→120→300 сек) + переинициализация `GoogleDriveService()` после каждого network error
- **Файлы изменены:** `drive_markdown_converter/main.py` → метод `run_daemon_loop()`

---

## ✅ RESOLVED: ImportError SUPPORTED_EXTENSIONS
- **Дата:** 2026-09-01
- **Агент:** drive_markdown_converter/main.py
- **Симптом:** `ImportError: cannot import name 'SUPPORTED_EXTENSIONS' from 'config'`
- **Причина:** `SUPPORTED_EXTENSIONS` не был определён в config.py (забыт при первичном создании)
- **Решение:** Добавлен `SUPPORTED_EXTENSIONS = {".pdf", ".docx", ...}` в config.py
- **Файлы изменены:** `drive_markdown_converter/config.py`

---

## 📝 KNOWN LIMITATION: NotebookLM без API
- **Дата:** 2026-09-02
- **Тип:** Архитектурное ограничение (не ошибка)
- **Описание:** Google NotebookLM не имеет публичного API для программной загрузки источников
- **Решение:** Полуавтоматическая схема: Drive Converter автоматически конвертирует файлы в MD и кладёт в `02_FOR_NOTEBOOK`. Пользователь **один раз вручную** добавляет эту папку как источник в NotebookLM UI.
- **Статус:** Принято как ограничение, зафиксировано в архитектуре
