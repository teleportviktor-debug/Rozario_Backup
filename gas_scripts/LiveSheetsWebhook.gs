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
    
    // ⚡ AUTO-EMAIL PROPOSAL for TIER 1 VIP leads (score ≥ 80%)
    if (score >= 80 && email && email !== "—" && email.indexOf("@") > 0) {
      sendProposalEmail(email, clientName, pkgName, priceUsd, niche, nowStr);
      // Update status in sheet
      sheet.getRange(lastRow, 11).setValue("📧 КП отправлено");
      // Notify via Telegram
      sendTelegram("📧 *AUTO-EMAIL КП отправлено!*\n👤 " + clientName + "\n📧 `" + email + "`\n📦 " + pkgName);
    }
    
    return ContentService.createTextOutput(JSON.stringify({
      status: "success",
      row: lastRow,
      lead_id: leadId,
      proposal_sent: score >= 80 && email && email !== "—"
    })).setMimeType(ContentService.MimeType.JSON);
    
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "error",
      message: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Auto-send branded HTML Proposal Email to TIER 1 VIP leads
 */
function sendProposalEmail(clientEmail, clientName, packageName, priceUsd, niche, dateStr) {
  var subject = "💎 Персональное коммерческое предложение для " + clientName + " • Razum AI";
  
  var htmlBody = '<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body style="margin:0; padding:0; background:#090d16; font-family:Arial,sans-serif;">' +
    '<div style="max-width:640px; margin:0 auto; padding:32px 20px;">' +
    
    // Header
    '<div style="background:rgba(15,23,42,0.95); border:1px solid rgba(255,255,255,0.1); border-radius:16px; padding:32px; margin-bottom:20px;">' +
    '<div style="display:inline-block; padding:4px 12px; border-radius:999px; font-size:11px; font-weight:800; background:rgba(16,185,129,0.15); color:#10b981; border:1px solid rgba(16,185,129,0.3); margin-bottom:16px;">💎 ПЕРСОНАЛЬНЫЙ GRAND SLAM ОФФЕР</div>' +
    '<h1 style="color:#f8fafc; font-size:24px; margin:0 0 8px;">Автоматизация для «' + clientName + '»</h1>' +
    '<p style="color:#94a3b8; font-size:14px; margin:0;">Отрасль: <strong>' + niche + '</strong> • Дата: <strong>' + dateStr + '</strong></p>' +
    '</div>' +
    
    // Metrics
    '<div style="display:flex; gap:12px; margin-bottom:20px;">' +
    '<div style="flex:1; background:rgba(15,23,42,0.95); border:1px solid rgba(255,255,255,0.1); border-radius:12px; padding:16px; text-align:center;">' +
    '<div style="color:#06b6d4; font-size:20px; font-weight:800;">$' + (priceUsd * 6) + '/мес</div>' +
    '<div style="color:#94a3b8; font-size:11px;">Экономия на рутине</div></div>' +
    '<div style="flex:1; background:rgba(15,23,42,0.95); border:1px solid rgba(255,255,255,0.1); border-radius:12px; padding:16px; text-align:center;">' +
    '<div style="color:#06b6d4; font-size:20px; font-weight:800;">5 дней</div>' +
    '<div style="color:#94a3b8; font-size:11px;">Срок окупаемости</div></div>' +
    '<div style="flex:1; background:rgba(15,23,42,0.95); border:1px solid rgba(255,255,255,0.1); border-radius:12px; padding:16px; text-align:center;">' +
    '<div style="color:#06b6d4; font-size:20px; font-weight:800;">$' + (priceUsd * 72) + '</div>' +
    '<div style="color:#94a3b8; font-size:11px;">Чистая выгода / год</div></div>' +
    '</div>' +
    
    // Package
    '<div style="background:rgba(15,23,42,0.95); border:1px solid rgba(255,255,255,0.1); border-radius:16px; padding:32px; margin-bottom:20px;">' +
    '<h2 style="color:#fff; font-size:18px; margin:0 0 16px;">📦 Тариф: ' + packageName + '</h2>' +
    '<ul style="list-style:none; padding:0; margin:0; color:#cbd5e1; font-size:14px; line-height:2;">' +
    '<li>✓ Суверенный контур в вашем Google Workspace — без чужих серверов</li>' +
    '<li>✓ Zero-Log архитектура — ваши данные остаются только у вас</li>' +
    '<li>✓ Автономные AI-агенты работают 24/7 по расписанию</li>' +
    '<li>✓ Пожизненная лицензия без ежемесячных подписок</li>' +
    '<li>✓ 60 дней инженерного сопровождения под ключ</li>' +
    '</ul></div>' +
    
    // CTA
    '<div style="background:linear-gradient(135deg, rgba(16,185,129,0.12), rgba(99,102,241,0.12)); border:1px solid rgba(16,185,129,0.4); border-radius:16px; padding:24px; text-align:center;">' +
    '<div style="color:#94a3b8; font-size:13px; margin-bottom:8px;">Единоразовая инвестиция (без подписок):</div>' +
    '<div style="color:#fff; font-size:28px; font-weight:800; margin-bottom:16px;">$' + priceUsd + ' <span style="font-size:13px; color:#10b981;">(Разово навсегда)</span></div>' +
    '<a href="mailto:razum.ai.pro@gmail.com?subject=Согласование ' + packageName + ' для ' + clientName + '" style="display:inline-block; padding:12px 28px; background:#10b981; color:#000; font-weight:800; border-radius:10px; text-decoration:none; font-size:14px;">Утвердить и Развернуть 🚀</a>' +
    '</div>' +
    
    // Footer
    '<p style="color:#475569; font-size:11px; text-align:center; margin-top:24px;">Razum Google AI PRO • Sovereign Automation 2026<br>Это автоматическое коммерческое предложение, сформированное системой Hormozi Scoring Engine.</p>' +
    
    '</div></body></html>';
  
  try {
    MailApp.sendEmail({
      to: clientEmail,
      subject: subject,
      htmlBody: htmlBody,
      name: "Razum AI • Sovereign Automation"
    });
    Logger.log("Proposal email sent to: " + clientEmail);
  } catch (e) {
    Logger.log("Email send error: " + e.toString());
    sendTelegram("⚠️ *Ошибка отправки КП по email:* " + e.toString());
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
