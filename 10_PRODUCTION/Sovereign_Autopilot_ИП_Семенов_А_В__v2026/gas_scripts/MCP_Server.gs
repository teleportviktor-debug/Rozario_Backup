/**
 * ============================================================================
 * RAZUM SOVEREIGN AI - MODEL CONTEXT PROTOCOL (MCP) SERVER FOR GAS
 * Status: Active / Enterprise Core
 * Allows Gemini / Antigravity Agents to safely interact with Google Workspace
 * ============================================================================
 */

function doPost(e) {
  try {
    const request = JSON.parse(e.postData.contents);
    const method = request.method;
    const params = request.params || {};

    let responseData = {};

    switch (method) {
      case "tools/list":
        responseData = {
          tools: [
            {
              name: "read_registry",
              description: "Чтение последних записей из финансового реестра или CRM",
              inputSchema: {
                type: "object",
                properties: { sheetName: { type: "string" }, limit: { type: "number" } }
              }
            },
            {
              name: "append_invoice",
              description: "Безопасная запись проверенного счета в таблицу",
              inputSchema: {
                type: "object",
                properties: {
                  vendor: { type: "string" },
                  inn: { type: "string" },
                  invoiceNumber: { type: "string" },
                  amount: { type: "number" }
                },
                required: ["vendor", "amount"]
              }
            },
            {
              name: "create_draft_reply",
              description: "Создание черновика письма в Gmail без непосредственной отправки",
              inputSchema: {
                type: "object",
                properties: {
                  threadId: { type: "string" },
                  body: { type: "string" }
                },
                required: ["threadId", "body"]
              }
            }
          ]
        };
        break;

      case "tools/call":
        responseData = executeMcpTool(params.name, params.arguments);
        break;

      default:
        throw new Error("Неизвестный MCP метод: " + method);
    }

    return ContentService.createTextOutput(JSON.stringify({ jsonrpc: "2.0", result: responseData }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ jsonrpc: "2.0", error: { code: -32603, message: err.message } }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function executeMcpTool(name, args) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  if (name === "append_invoice") {
    const sheet = ss.getSheetByName(CONFIG.INVOICE_SHEET_NAME) || ss.getActiveSheet();
    sheet.appendRow([
      new Date(),
      args.invoiceNumber || "Б/Н",
      args.vendor,
      args.inn || "-",
      args.amount,
      0,
      "MCP-VERIFIED",
      "ACTIVE"
    ]);
    return { status: "success", message: "Счет успешно добавлен через MCP Server" };
  }

  if (name === "read_registry") {
    const sheet = ss.getSheetByName(args.sheetName || CONFIG.INVOICE_SHEET_NAME);
    if (!sheet) return { status: "error", message: "Лист не найден" };
    const data = sheet.getDataRange().getValues();
    return { status: "success", rows: data.slice(- (args.limit || 5)) };
  }

  return { status: "error", message: "Инструмент не поддерживается" };
}
