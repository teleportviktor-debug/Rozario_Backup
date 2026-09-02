/**
 * ============================================================================
 * RAZUM SOVEREIGN AI ECOSYSTEM 2026 - MASTER GOOGLE APPS SCRIPT (GAS) CORE
 * Status: Production Ready (v2.6)
 * Integration: Google Workspace + Gemini Flash Lite + Antigravity Engine
 * ============================================================================
 */

// Global Configuration
const CONFIG = {
  GEMINI_API_KEY: PropertiesService.getScriptProperties().getProperty("GEMINI_API_KEY") || "",
  GEMINI_MODEL: "gemini-3.5-flash-lite", // Optimized for ultra-low cost and sub-second speed
  REGISTRY_SHEET_NAME: "Реестр_Автоматизации",
  INVOICE_SHEET_NAME: "Реестр_Счетов",
  LEADS_SHEET_NAME: "CRM_Лиды"
};

/**
 * Initial Setup: Creates required sheets, headers and formatting in the active spreadsheet
 */
function setupSovereignWorkspace() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // 1. Setup Invoice Sheet
  let invSheet = ss.getSheetByName(CONFIG.INVOICE_SHEET_NAME);
  if (!invSheet) {
    invSheet = ss.insertSheet(CONFIG.INVOICE_SHEET_NAME);
    invSheet.appendRow(["Дата", "Номер Счета", "Контрагент", "ИНН", "Сумма (₽)", "НДС (₽)", "Хеш Безопасности", "Статус"]);
    invSheet.getRange("A1:H1").setBackground("#0f172a").setFontColor("#10b981").setFontWeight("bold");
    invSheet.setFrozenRows(1);
  }

  // 2. Setup Leads Sheet with Hormozi Score Column
  let leadSheet = ss.getSheetByName(CONFIG.LEADS_SHEET_NAME);
  if (!leadSheet) {
    leadSheet = ss.insertSheet(CONFIG.LEADS_SHEET_NAME);
    leadSheet.appendRow(["Дата/Время", "Имя/Компания", "Email / TG", "Боль (1-10)", "Бюджет (1-10)", "ЛПР (1-10)", "Срочность (1-10)", "Hormozi Score %", "Tier Сделки", "Оффер"]);
    leadSheet.getRange("A1:J1").setBackground("#0f172a").setFontColor("#38bdf8").setFontWeight("bold");
    leadSheet.setFrozenRows(1);
  }

  Logger.log("✅ Суверенный контур Google Workspace успешно инициализирован.");
}

/**
 * Universal Gemini API Caller (Structured Output Mode)
 */
function callGemini(prompt, schemaJson) {
  const apiKey = CONFIG.GEMINI_API_KEY;
  if (!apiKey) {
    throw new Error("❌ Ключ GEMINI_API_KEY не установлен в Script Properties!");
  }

  const url = `https://generativelanguage.googleapis.com/v1beta/models/${CONFIG.GEMINI_MODEL}:generateContent?key=${apiKey}`;

  const payload = {
    contents: [{ parts: [{ text: prompt }] }],
    generationConfig: {
      temperature: 0.1,
      responseMimeType: "application/json"
    }
  };

  const options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  const response = UrlFetchApp.fetch(url, options);
  const responseData = JSON.parse(response.getContentText());

  if (responseData.candidates && responseData.candidates[0].content) {
    return JSON.parse(responseData.candidates[0].content.parts[0].text);
  } else {
    throw new Error("Ошибка вызова Gemini: " + response.getContentText());
  }
}
