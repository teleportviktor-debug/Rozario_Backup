/**
 * SPEECH & CALL ANALYTICS ENGINE (GEMINI TRANSCRIBE & SCRIPT AUDITOR)
 * Analyzes audio recordings of sales reps, scores script compliance and flags deal blockers
 */

class SpeechAuditorEngine {
  constructor() {
    this.sampleAudits = [
      {
        manager: 'Алексей Смирнов (Менеджер ОП)',
        client: 'ООО "ПромТех" (Гендиректор)',
        duration: '04:32',
        score: 92,
        criteria: [
          { name: 'Приветствие и регламент', passed: true, comment: 'Четкое введение и обозначение регламента 5 минут' },
          { name: 'Выявление боли (Рутина/ФОТ)', passed: true, comment: 'Зафиксировано 3 часа потерь бухгалтера ежедневно' },
          { name: 'Презентация суверенного контура', passed: true, comment: 'Сделан акцент на Zero-Log и разовую оплату' },
          { name: 'Обработка возражения по цене', passed: true, comment: 'Приведен расчет ROI: окупаемость за 7 дней' },
          { name: 'Четкий следующий шаг (CTA)', passed: true, comment: 'Назначена отправка КП с согласованием в A2UI' }
        ],
        summary: 'Идеальный звонок по формуле Гормози. Лид квалифицирован как TIER 1 VIP. Сделка закроется сегодня.'
      },
      {
        manager: 'Дмитрий Ковалев (Junior SDR)',
        client: 'ИП Михайлов (Сеть кофеен)',
        duration: '02:45',
        score: 54,
        criteria: [
          { name: 'Приветствие и регламент', passed: true, comment: 'Стандартно' },
          { name: 'Выявление боли (Рутина/ФОТ)', passed: false, comment: '❌ Не спросил про объем счетов в месяц' },
          { name: 'Презентация суверенного контура', passed: false, comment: '❌ Начал объяснять технический стек вместо выгоды' },
          { name: 'Обработка возражения по цене', passed: false, comment: '❌ Смутился при вопросе о скидке' },
          { name: 'Четкий следующий шаг (CTA)', passed: true, comment: 'Договорился о повторном звонке' }
        ],
        summary: 'Нарушение регламента презентации. Рекомендуется включить динамический телесуфлер Teleprompter Studio.'
      }
    ];
  }

  getAudit(index = 0) {
    return this.sampleAudits[index] || this.sampleAudits[0];
  }
}

window.SpeechAuditorEngine = new SpeechAuditorEngine();
