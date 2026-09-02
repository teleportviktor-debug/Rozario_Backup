/**
 * VISUAL SOVEREIGN PASSPORT & SECURITY CERTIFICATE GENERATOR
 * Renders an official cryptographic certificate on HTML5 Canvas
 */

class PassportGeneratorEngine {
  renderCertificate(canvasId, clientName, packageName, sha256Hash) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    canvas.width = 800;
    canvas.height = 550;

    // Background
    ctx.fillStyle = '#090d16';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Border Glow & Frame
    ctx.strokeStyle = '#10b981';
    ctx.lineWidth = 4;
    ctx.strokeRect(20, 20, canvas.width - 40, canvas.height - 40);

    ctx.strokeStyle = 'rgba(99, 102, 241, 0.4)';
    ctx.lineWidth = 1;
    ctx.strokeRect(28, 28, canvas.width - 56, canvas.height - 56);

    // Header
    ctx.fillStyle = '#34d399';
    ctx.font = 'bold 22px Plus Jakarta Sans, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('СЕРТИФИКАТ СУВЕРЕННОГО AI-КОНТУРА 2026', canvas.width / 2, 70);

    ctx.fillStyle = '#94a3b8';
    ctx.font = '12px Plus Jakarta Sans, sans-serif';
    ctx.fillText('GOOGLE ENTERPRISE TRUSTED PERIMETER • ZERO-LOG POLICY', canvas.width / 2, 95);

    // Divider
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.beginPath();
    ctx.moveTo(60, 115);
    ctx.lineTo(canvas.width - 60, 115);
    ctx.stroke();

    // Body Text
    ctx.fillStyle = '#f8fafc';
    ctx.font = '14px Plus Jakarta Sans, sans-serif';
    ctx.fillText('Настоящим удостоверяется, что суверенная AI-экосистема развернута для:', canvas.width / 2, 150);

    ctx.fillStyle = '#38bdf8';
    ctx.font = 'bold 26px Plus Jakarta Sans, sans-serif';
    ctx.fillText(clientName || 'ООО "ПРЕДПРИЯТИЕ БУДУЩЕГО"', canvas.width / 2, 195);

    ctx.fillStyle = '#94a3b8';
    ctx.font = '14px Plus Jakarta Sans, sans-serif';
    ctx.fillText('Пакет конфигурации:', canvas.width / 2, 235);

    ctx.fillStyle = '#a855f7';
    ctx.font = 'bold 18px Plus Jakarta Sans, sans-serif';
    ctx.fillText(packageName || '«Суверенный Автопилот Бизнеса 2026»', canvas.width / 2, 265);

    // Security Metrics Box
    ctx.fillStyle = 'rgba(15, 23, 42, 0.8)';
    ctx.fillRect(80, 300, canvas.width - 160, 120);
    ctx.strokeStyle = 'rgba(16, 185, 129, 0.3)';
    ctx.strokeRect(80, 300, canvas.width - 160, 120);

    ctx.textAlign = 'left';
    ctx.fillStyle = '#10b981';
    ctx.font = 'bold 12px JetBrains Mono, monospace';
    ctx.fillText('✓ Хранение файлов: ИСКЛЮЧИТЕЛЬНО В GOOGLE DRIVE КЛИЕНТА', 100, 330);
    ctx.fillText('✓ Вычислительное ядро: AIR-GAPPED PYTHON (ANTIGRAVITY)', 100, 355);
    ctx.fillText('✓ Авторизация: GOOGLE APPS SCRIPT SCRIPT PROPERTIES (ZERO-LEAK)', 100, 380);
    ctx.fillText('✓ Криптографический хеш: ' + (sha256Hash || 'sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855').substring(0, 38) + '...', 100, 405);

    // Footer & Signature
    ctx.textAlign = 'center';
    ctx.fillStyle = '#64748b';
    ctx.font = '11px Plus Jakarta Sans, sans-serif';
    const dateStr = new Date().toLocaleDateString('ru-RU', { year: 'numeric', month: 'long', day: 'numeric' });
    ctx.fillText(`Дата выдачи: ${dateStr} • Razum Intelligent AI Core 2026`, canvas.width / 2, 475);

    // Gold Stamp/Seal simulation
    ctx.beginPath();
    ctx.arc(canvas.width - 120, 460, 36, 0, 2 * Math.PI);
    ctx.fillStyle = 'rgba(16, 185, 129, 0.15)';
    ctx.fill();
    ctx.strokeStyle = '#10b981';
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.fillStyle = '#34d399';
    ctx.font = 'bold 9px JetBrains Mono, monospace';
    ctx.fillText('VERIFIED', canvas.width - 120, 456);
    ctx.fillText('SOVEREIGN', canvas.width - 120, 468);
  }
}

window.PassportGeneratorEngine = new PassportGeneratorEngine();
