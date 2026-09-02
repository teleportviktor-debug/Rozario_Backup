/**
 * HORMOZI LEAD SCORER & ROI COMPUTATION ENGINE (ANTIGRAVITY AIR-GAPPED CORE)
 * Mathematical Evaluation based on Alex Hormozi 4-Factor Scale & Grand Slam Offer Architecture
 */

class HormoziEngine {
  constructor() {
    this.weights = {
      pain: 0.35,
      purchasingPower: 0.25,
      decisionMaking: 0.20,
      urgency: 0.20
    };
  }

  calculateLeadScore(pain, purchasingPower, decisionMaking, urgency) {
    const rawScore = (
      (pain * this.weights.pain) +
      (purchasingPower * this.weights.purchasingPower) +
      (decisionMaking * this.weights.decisionMaking) +
      (urgency * this.weights.urgency)
    );

    const scorePercent = Math.round((rawScore / 10) * 100);

    let tier = '';
    let tierColor = '';
    let recommendation = '';

    if (scorePercent >= 80) {
      tier = '🔥 TIER 1: VIP ПРИОРИТЕТ (ЗАКРЫВАТЬ СЕГОДНЯ)';
      tierColor = 'var(--emerald-400)';
      recommendation = 'Высокая боль и бюджет. Назначать персональный демо-созвон с фаундером. Предлагать пакет "Sovereign Autopilot" ($300) или "Genesis Enterprise" ($500).';
    } else if (scorePercent >= 60) {
      tier = '⚡ TIER 2: ВЫСОКАЯ ВЕРОЯТНОСТЬ (СДЕЛКА 48 ЧАСОВ)';
      tierColor = 'var(--cyan-400)';
      recommendation = 'Квалифицированный лид. Предлагать пакет с разовой оплатой ("Command Center" $100 или "Intelligence Module" $200).';
    } else if (scorePercent >= 40) {
      tier = '⏳ TIER 3: ПРОГРЕВ И АВТОМАТИЗАЦИЯ';
      tierColor = 'var(--amber-400)';
      recommendation = 'Низкая срочность или бюджет. Направить стартовый пакет "Spark Starter" за $50 и включить в цепочку контент-прогрева.';
    } else {
      tier = '❌ НЕ ЦЕЛЕВОЙ (ОТКЛОНИТЬ / АВТО-ОТВЕТ)';
      tierColor = 'var(--rose-500)';
      recommendation = 'Не тратить время менеджеров. Отправить ссылку на бесплатные материалы.';
    }

    return {
      scorePercent,
      rawScore: rawScore.toFixed(2),
      tier,
      tierColor,
      recommendation
    };
  }

  calculateROI(employeesCount, avgSalaryUsd, manualHoursPerDay, packageCostUsd = 300) {
    const hourlyRate = avgSalaryUsd / (21 * 8); // 21 working days, 8h/day
    const savedHoursPerMonth = employeesCount * manualHoursPerDay * 21 * 0.8; // 80% automated
    const monthlySavingsUsd = Math.round(savedHoursPerMonth * hourlyRate);
    const annualSavingsUsd = monthlySavingsUsd * 12;
    const netFirstYearProfit = annualSavingsUsd - packageCostUsd;
    const paybackDays = Math.max(1, Math.round((packageCostUsd / (monthlySavingsUsd / 30))));
    const roiMultiplier = ((annualSavingsUsd / packageCostUsd) * 100).toFixed(0);

    return {
      hourlyRate: Math.round(hourlyRate),
      savedHoursPerMonth: Math.round(savedHoursPerMonth),
      monthlySavingsUsd,
      annualSavingsUsd,
      netFirstYearProfit,
      paybackDays,
      roiMultiplier
    };
  }

  generateGrandSlamOffers(clientName, niche, mainPain, budgetUsd) {
    return [
      {
        title: `🏆 Оффер #1: «Sovereign Autopilot — ${niche}»`,
        tagline: '100% Устранение рутины с гарантией окупаемости',
        formula: {
          dreamOutcome: `Полное освобождение ${niche} от ручного разбора ${mainPain}`,
          likelihood: 'Развертывание в суверенном контуре Google Workspace без передачи паролей',
          timeDelay: 'Первый работающий результат через 24 часа',
          effortSacrifice: 'Нулевые затраты времени: настройка "под ключ" нашими инженерами'
        },
        price: '$300 (разово)',
        cta: 'Внедрить за 24 часа'
      },
      {
        title: `⚡ Оффер #2: «Intelligence Module & Hormozi Scorer»`,
        tagline: 'Увеличение конверсии отдела продаж в 2.4 раза',
        formula: {
          dreamOutcome: 'Менеджеры закрывают сделки по математически выверенным скриптам',
          likelihood: 'Оценка каждого звонка алгоритмом Gemini Flash Structured Output',
          timeDelay: 'Готовый отчет по каждому звонку через 3 секунды после завершения',
          effortSacrifice: 'Работает прямо в существующих Google Sheets без обучения CRM'
        },
        price: '$200 (разово)',
        cta: 'Подключить отдел продаж'
      },
      {
        title: `🧬 Оффер #3: «Genesis Enterprise Ecosystem»`,
        tagline: 'Индивидуальный суверенный контур с Antigravity Swarm',
        formula: {
          dreamOutcome: 'Комплексная AI-экосистема с математической гарантией отсутствия галлюцинаций',
          likelihood: 'Air-Gapped Python среда с сертифицированным контуром безопасности Zero-Log',
          timeDelay: '3 дня до полноценного боевого запуска',
          effortSacrifice: 'Персональный инженер и поддержка без подписок'
        },
        price: '$500 (разово)',
        cta: 'Заказать Enterprise аудит'
      }
    ];
  }
}

window.HormoziEngine = new HormoziEngine();
