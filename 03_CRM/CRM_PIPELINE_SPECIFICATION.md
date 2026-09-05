---
authority_level: "CANONICAL_TRUTH"
document_type: "CRM_PIPELINE_SPECIFICATION"
project: "Razum Google AI PRO"
last_audit_utc: "2026-09-04T22:20:00Z"
target_system: "NotebookLM Grounding & CRM Sync"
---

# 📊 03_CRM • Регламент ведения сделок и интеграции с Google Workspace

Настоящий документ регламентирует структуру хранения лидов, этапы воронки и Zero Trust протоколы работы с клиентскими данными.

---

## 1. Этапы суверенной воронки продаж (Sovereign Pipeline Stages)

| Этап ID | Название этапа | Триггер перехода | Обязательный артефакт |
| :--- | :--- | :--- | :--- |
| `STAGE_01` | **Raw Discovery** | Запрос через API/Webhook | Pydantic-валидация входящего JSON |
| `STAGE_02` | **Zero Trust Audit** | Проверка токена `ntn_...` | Автоматическое маскирование PII (PaliGemma 2) |
| `STAGE_03` | **Hormozi 4-Scale Score** | Расчет баллов (Pain, Power, Decision, Urgency) | A2UI карточка с метриками и ARR |
| `STAGE_04` | **Sovereign Proposal** | Интегральный скоринг >= 90 | Персонализированный 9:16 видео-питч и Google Card |
| `STAGE_05` | **Contract & Deployment** | Согласование условий с CTO/CEO | Развертывание контура на Google Cloud клиента |

---

## 2. Интеграция с Google Таблицами через n8n

Канонический идентификатор рабочей таблицы лидов:
* **Google Spreadsheet ID:** `1fVe94GnUznuIVZr71hK561GMICQs9dt9qXHaPzINk7M`
* **Workflow файл:** [`n8n_workflow_dynamic_outreach_sheets.json`](file:///c:/Users/user/ГУГЛ%20ИМПЕРИЯ/n8n_workflow_dynamic_outreach_sheets.json)

| Узел n8n | Тип узла | Параметр привязки ID | Назначение |
| :--- | :--- | :--- | :--- |
| **Google Sheets Trigger** | `googleSheetsTrigger` | `documentId: 1fVe94GnUznuIVZr71hK561GMICQs9dt9qXHaPzINk7M` | Мониторинг новых лидов (rowAdded) |
| **Generate Personalized Reel** | `httpRequest` | `POST /api/v1/outreach/dispatch` | Параметрический видео-рендер + CardsV2 |
| **Write Video Link to Sheet** | `googleSheets` | `documentId: 1fVe94GnUznuIVZr71hK561GMICQs9dt9qXHaPzINk7M` | Запись `video_url` и `email_subject` в строку |
| **Mark Status Draft Ready** | `googleSheets` | `documentId: 1fVe94GnUznuIVZr71hK561GMICQs9dt9qXHaPzINk7M` | Смена статуса на `Draft Ready` |

---

## STRICT_BOUNDARIES

1. Если в запросе о статусе лида отсутствуют верифицированные метаданные воронки, модель обязана вернуть точный токен: **`[NO_GROUNDED_DATA]`**.
2. Запрещено передавать персональные данные (PII) без предварительного маскирования.
