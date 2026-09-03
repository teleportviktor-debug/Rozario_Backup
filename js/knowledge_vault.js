/**
 * CORPORATE KNOWLEDGE VAULT & RAG SEARCH INDEXER (GEMINI NOTEBOOK 300 SOURCES)
 * Indexes company folders and provides instant search with grounded citations
 */

class KnowledgeVaultEngine {
  constructor() {
    this.vault = [
      {
        folder: '01_STRATEGY',
        file: '2026_MASTER_ROADMAP_90_DAYS.md',
        category: 'Стратегия',
        title: 'Мастер-Дорожная Карта на 90 Дней',
        snippet: 'Фаза 1: Развертывание ядра и MCP GAS Сервера. Фаза 2: A2UI и фоновые 24/7 агенты Gemini Spark. Фаза 3: Self-Healing шлюз и Enterprise контуры.',
        tags: ['roadmap', 'kpi', 'mcp', 'spark']
      },
      {
        folder: '02_BRAND_BOOK',
        file: 'SOVEREIGN_BRAND_IDENTITY_2026.md',
        category: 'Бренд',
        title: 'Суверенный Бренд-Бук и Цветовой Код',
        snippet: 'Cyber Emerald (#10b981), Deep Space Navy (#090d16). Философия: 100% суверенитет данных, отказ от ежемесячных подписок (No-SaaS), математика без галлюцинаций.',
        tags: ['brand', 'colors', 'manifesto', 'no-saas']
      },
      {
        folder: '04_SALES_PLAYBOOK',
        file: 'GRAND_SLAM_SCRIPTS_AND_OBJECTIONS.md',
        category: 'Продажи',
        title: 'Grand Slam Офферы и Скрипты Продаж',
        snippet: 'Отработка возражения "80% бизнеса разочарованы в AI". Закрытие сделок на пакеты 14 900 ₽ и 19 900 ₽ с 14-дневной гарантией возврата денег.',
        tags: ['sales', 'hormozi', 'objections', 'scripts']
      },
      {
        folder: '06_SOP_REGLAMENTS',
        file: 'ZERO_LOG_SECURITY_SOP.md',
        category: 'Безопасность',
        title: 'Регламент Zero-Log и Изоляция Данных',
        snippet: 'Обработка документов исключительно в оперативной памяти Google Apps Script. Хранение ключей в Script Properties. SHA-256 хеширование.',
        tags: ['security', 'zero-log', 'gdpr', 'confidentiality']
      },
      {
        folder: '07_FINANCIAL_MODELS',
        file: 'UNIT_ECONOMICS_AND_PRICING.json',
        category: 'Финансы',
        title: 'Юнит-Экономика и Маржинальность Пакетов',
        snippet: 'Маржинальность пакетов от 83.6% до 91.5%. Плановая чистая прибыль: 1 226 050 ₽/мес при 220 разовых продажах.',
        tags: ['finance', 'roi', 'pricing', 'margin']
      }
    ];
  }

  search(query) {
    if (!query || query.trim() === '') return this.vault;
    const q = query.toLowerCase();
    return this.vault.filter(item => 
      item.title.toLowerCase().includes(q) ||
      item.snippet.toLowerCase().includes(q) ||
      item.tags.some(t => t.includes(q)) ||
      item.folder.toLowerCase().includes(q)
    );
  }
}

window.KnowledgeVaultEngine = new KnowledgeVaultEngine();
