/**
 * ============================================================================
 * RAZUM AI 2026 • LIVE GOOGLE SHEETS CRM WEBHOOK & AUTO-INSERT ENGINE (v2.6)
 * Receives Orders from Landing Pages & Appends Formatted Rows in Real Time
 * ============================================================================
 */

// 1. CONFIGURATION
var TELEGRAM_BOT_TOKEN = "8746018179:AAHBqzasizNCw3pw9gMpVb5yvr1uikY07OU";
var TELEGRAM_CHAT_ID = "7655208225";
var SHEET_NAME = "CRM_LEADS_2026";

/**
 * Auto-initialize, style and configure Google Sheet with chips, validations & conditional formatting
 */
function setupSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);
  
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
  }
  
  sheet.clear();
  sheet.clearConditionalFormatRules();
  
  var headers = [
    ["ID Заявки", "Дата и Время", "Клиент / Компания", "Ниша", "Email", "Телефон / Telegram", "Тариф", "Сумма ($)", "Hormozi Скоринг", "Категория", "Статус Сделки", "Пакет Собран"]
  ];
  
  var headerRange = sheet.getRange(1, 1, 1, headers[0].length);
  headerRange.setValues(headers);
  headerRange.setBackground("#1e293b");
  headerRange.setFontColor("#34d399");
  headerRange.setFontWeight("bold");
  headerRange.setFontFamily("Roboto");
  headerRange.setHorizontalAlignment("center");
  headerRange.setVerticalAlignment("middle");
  
  sheet.setRowHeight(1, 40);
  sheet.setFrozenRows(1);
  
  // Set Column Widths (Optimal padding)
  sheet.setColumnWidth(1, 140); // ID
  sheet.setColumnWidth(2, 160); // Date
  sheet.setColumnWidth(3, 220); // Client
  sheet.setColumnWidth(4, 170); // Niche
  sheet.setColumnWidth(5, 220); // Email
  sheet.setColumnWidth(6, 190); // Phone
  sheet.setColumnWidth(7, 200); // Package
  sheet.setColumnWidth(8, 110); // Price
  sheet.setColumnWidth(9, 130); // Score
  sheet.setColumnWidth(10, 180); // Tier
  sheet.setColumnWidth(11, 180); // Status
  sheet.setColumnWidth(12, 140); // Built
  
  // 1. Data Validation: Categories (Dropdown Chips)
  var tierRule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["🔥 TIER 1: VIP", "⚡ TIER 2: HOT", "❄️ TIER 3: WARM"], true)
    .setAllowInvalid(false)
    .build();
  sheet.getRange("J2:J500").setDataValidation(tierRule);
  
  // 2. Data Validation: Deal Status (Dropdown Chips)
  var statusRule = SpreadsheetApp.newDataValidation()
    .requireValueInList([
      "🆕 Новая заявка", 
      "📞 В обработке", 
      "📦 Пакет собран", 
      "💰 Оплачено", 
      "🤝 Закрыто успешно", 
      "❌ Отказ"
    ], true)
    .setAllowInvalid(false)
    .build();
  sheet.getRange("K2:K500").setDataValidation(statusRule);

  // 3. Conditional Formatting: Highlight VIP Tier 1
  var vipRule = SpreadsheetApp.newConditionalFormatRule()
    .whenFormulaSatisfied('=$J2="🔥 TIER 1: VIP"')
    .setBackground("#ecfdf5")
    .setFontColor("#065f46")
    .setRanges([sheet.getRange("A2:L500")])
    .build();

  var hotRule = SpreadsheetApp.newConditionalFormatRule()
    .whenFormulaSatisfied('=$J2="⚡ TIER 2: HOT"')
    .setBackground("#fefce8")
    .setFontColor("#854d0e")
    .setRanges([sheet.getRange("A2:L500")])
    .build();

  sheet.setConditionalFormatRules([vipRule, hotRule]);

  // Insert Sample Verification Leads
  var sampleRows = [
    ["LEAD-101", "02.09.2026 23:15:38", "ООО «ПромТехИнвест»", "Производство и Поставки", "ceo@promtech-invest.ru", "+7 (999) 123-45-67", "Sovereign Autopilot ($300)", 300, "88%", "🔥 TIER 1: VIP", "📦 Пакет собран", "ДА (10_PRODUCTION)"],
    ["LEAD-102", "02.09.2026 23:45:10", "ИП Семенов А.В.", "SEO и Маркетинг", "semenov@smarty-seo.ru", "+7 (916) 444-22-11", "Intelligence Module ($200)", 200, "86%", "🔥 TIER 1: VIP", "💰 Оплачено", "ДА (10_PRODUCTION)"],
    ["LEAD-103", "03.09.2026 00:09:20", "Виктор Fullhouse", "AI Автоматизация", "viktor@fullhouse.vip", "+7 (999) 777-88-99", "Sovereign Autopilot ($300)", 300, "92%", "🔥 TIER 1: VIP", "🤝 Закрыто успешно", "ДА (10_PRODUCTION)"]
  ];

  sheet.getRange(2, 1, sampleRows.length, sampleRows[0].length).setValues(sampleRows);
  for (var r = 2; r <= 4; r++) {
    sheet.setRowHeight(r, 28);
  }

  SpreadsheetApp.getUi().alert("🎉 CRM_LEADS_2026 успешно настроена:\n\n✓ Темная шапка (#1E293B)\n✓ Выпадающие списки-чипы (Статусы и Категории)\n✓ Условное форматирование VIP-сделок\n✓ Демо-заявки занесены в реестр!");
}

/**
 * Webhook POST endpoint for incoming web orders
 */
function doPost(e) {
  try {
    var rawData = e.postData.contents;
    var data = JSON.parse(rawData);
    
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(SHEET_NAME);
    if (!sheet) {
      setupSheet();
      sheet = ss.getSheetByName(SHEET_NAME);
    }
    
    var nowStr = Utilities.formatDate(new Date(), "GMT+3", "dd.MM.yyyy HH:mm:ss");
    var leadId = data.id || ("WEB-" + new Date().getTime());
    var clientName = data.name || "Новый Клиент";
    var niche = data.niche || "B2B";
    var email = data.email || "—";
    var phone = data.phone || "—";
    var pkgName = data.package || "Sovereign Autopilot ($300)";
    var priceUsd = data.price_usd || 300;
    var score = data.score || 88;
    var tier = score >= 80 ? "🔥 TIER 1: VIP" : (score >= 60 ? "⚡ TIER 2: HOT" : "❄️ TIER 3: WARM");
    var status = "🆕 Новая заявка";
    var built = "ДА (10_PRODUCTION)";
    
    var rowData = [
      leadId, nowStr, clientName, niche, email, phone, pkgName, priceUsd, score + "%", tier, status, built
    ];
    
    sheet.appendRow(rowData);
    var lastRow = sheet.getLastRow();
    sheet.setRowHeight(lastRow, 28);
    
    var range = sheet.getRange(lastRow, 1, 1, rowData.length);
    range.setFontFamily("Roboto");
    range.setFontSize(10);
    range.setVerticalAlignment("middle");
    
    // Send Telegram Notification
    var tgMsg = "🔔 *НОВАЯ ЗАЯВКА В GOOGLE SHEETS CRM!*\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n" +
                "👤 *Клиент:* " + clientName + "\n" +
                "🏢 *Ниша:* " + niche + "\n" +
                "📧 *Email:* `" + email + "`\n" +
                "📞 *Телефон:* `" + phone + "`\n" +
                "📦 *Тариф:* *" + pkgName + "*\n" +
                "💰 *Сумма:* *$" + priceUsd + " (разово)*\n" +
                "🧮 *Hormozi Скоринг:* " + score + "% (" + tier + ")\n" +
                "⏰ *Время:* " + nowStr + "\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n" +
                "📊 *Запись добавлена в Google Таблицу*";
                
    sendTelegram(tgMsg);
    
    return ContentService.createTextOutput(JSON.stringify({
      status: "success",
      row: lastRow,
      lead_id: leadId
    })).setMimeType(ContentService.MimeType.JSON);
    
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "error",
      message: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Send alert to Telegram via Bot API
 */
function sendTelegram(text) {
  if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) return;
  var url = "https://api.telegram.org/bot" + TELEGRAM_BOT_TOKEN + "/sendMessage";
  var payload = {
    chat_id: TELEGRAM_CHAT_ID,
    text: text,
    parse_mode: "Markdown"
  };
  try {
    UrlFetchApp.fetch(url, {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    });
  } catch (e) {
    Logger.log("Telegram error: " + e.toString());
  }
}
