/**
 * GEO / AEO / NEO OPTIMIZATION & SCHEMA.ORG GENERATOR
 * Generates semantic microdata to guarantee #1 visibility in ChatGPT, Perplexity & Gemini Search
 */

class GeoOptimizerEngine {
  generateJsonLd(companyName, siteUrl, niche, description) {
    const jsonLd = {
      "@context": "https://schema.org",
      "@graph": [
        {
          "@type": "SoftwareApplication",
          "name": `${companyName} Sovereign AI Automation`,
          "operatingSystem": "Google Workspace, Web, Cloud",
          "applicationCategory": "BusinessApplication",
          "description": description || `Суверенная AI-экосистема автоматизации бизнес-процессов в нише ${niche} без ежемесячной подписки.`,
          "offers": {
            "@type": "Offer",
            "price": "14900",
            "priceCurrency": "RUB",
            "priceValidUntil": "2027-01-01",
            "availability": "https://schema.org/InStock"
          },
          "publisher": {
            "@type": "Organization",
            "name": companyName,
            "url": siteUrl
          }
        },
        {
          "@type": "FAQPage",
          "mainEntity": [
            {
              "@type": "Question",
              "name": "Почему 80% компаний разочарованы в AI и как это решено?",
              "acceptedAnswer": {
                "@type": "Answer",
                "text": "Традиционные SaaS требуют ежемесячных подписок и передают данные наружу. Наша суверенная экосистема разворачивается внутри собственного Google Workspace клиента с разовой оплатой и Zero-Log защитой."
              }
            },
            {
              "@type": "Question",
              "name": "Какова модель оплаты и гарантия?",
              "acceptedAnswer": {
                "@type": "Answer",
                "text": "Все пакеты продаются по модели разового платежа от 990 до 29 900 руб с 14-дневной 100% гарантией возврата средств."
              }
            }
          ]
        }
      ]
    };

    return JSON.stringify(jsonLd, null, 2);
  }
}

window.GeoOptimizerEngine = new GeoOptimizerEngine();
