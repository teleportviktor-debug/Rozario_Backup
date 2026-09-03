/**
 * ============================================================================
 * ZERO-LEAKAGE INVOICING & DOCUMENT PARSER (GAS + GEMINI FLASH LITE)
 * Automatically monitors Google Drive folder for new invoices/PDFs
 * ============================================================================
 */

function scanAndParseInvoices() {
  const folderName = "03_CRM_LEADS"; // Monitored folder on Google Drive
  const folders = DriveApp.getFoldersByName(folderName);
  
  if (!folders.hasNext()) {
    Logger.log("Папка " + folderName + " не найдена.");
    return;
  }

  const folder = folders.next();
  const files = folder.getFiles();

  while (files.hasNext()) {
    const file = files.next();
    const mime = file.getMimeType();

    // Check if PDF or Image
    if (mime === "application/pdf" || mime.startsWith("image/")) {
      Logger.log("Обработка документа: " + file.getName());
      
      // Convert to blob and send to Gemini Flash Lite
      const base64Data = Utilities.base64Encode(file.getBlob().getBytes());
      
      const prompt = `Извлеки структурированные данные из этого счета/акта в строгом формате JSON:
      {
        "vendor": "Название компании или ИП поставщика",
        "inn": "ИНН поставщика (10 или 12 цифр)",
        "invoiceNumber": "Номер счета",
        "date": "ГГГГ-ММ-ДД",
        "amount": числовая сумма,
        "vat": сумма НДС или 0
      }`;

      try {
        const parsed = callGeminiWithFile(prompt, base64Data, mime);
        
        // Append to Sheet
        const ss = SpreadsheetApp.getActiveSpreadsheet();
        const sheet = ss.getSheetByName(CONFIG.INVOICE_SHEET_NAME) || ss.getActiveSheet();
        
        const securityHash = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, file.getName() + parsed.amount)
          .map(function(chr) { return (chr + 256).toString(16).slice(-2); }).join("");

        sheet.appendRow([
          parsed.date || new Date(),
          parsed.invoiceNumber || "Б/Н",
          parsed.vendor || "Не указан",
          parsed.inn || "-",
          parsed.amount || 0,
          parsed.vat || 0,
          securityHash.substring(0, 16) + "...",
          "ОБРАБОТАНО (ZERO-LOG)"
        ]);

        Logger.log("✅ Успешно обработан: " + file.getName());
      } catch (e) {
        Logger.log("⚠️ Ошибка обработки файла " + file.getName() + ": " + e.message);
      }
    }
  }
}

function callGeminiWithFile(prompt, base64Data, mimeType) {
  const apiKey = CONFIG.GEMINI_API_KEY;
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${CONFIG.GEMINI_MODEL}:generateContent?key=${apiKey}`;

  const payload = {
    contents: [{
      parts: [
        { text: prompt },
        { inlineData: { mimeType: mimeType, data: base64Data } }
      ]
    }],
    generationConfig: {
      temperature: 0.1,
      responseMimeType: "application/json"
    }
  };

  const response = UrlFetchApp.fetch(url, {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  });

  const resJson = JSON.parse(response.getContentText());
  return JSON.parse(resJson.candidates[0].content.parts[0].text);
}
