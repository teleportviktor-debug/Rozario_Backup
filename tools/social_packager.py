"""
============================================================================
RAZUM AI 2026 • SOCIAL CONTENT PACKAGER & MULTI-CHANNEL EXPORTER
Bundles Instagram, LinkedIn and Telegram campaigns with images & tags
============================================================================
"""

import os
import sys
import shutil
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT_DIR = os.path.join(ROOT_DIR, "10_PRODUCTION", "SOCIAL_EXPORT")
VISUALS_DIR = os.path.join(ROOT_DIR, "assets", "launch_visuals")

def package_social_campaign():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    batch_dir = os.path.join(EXPORT_DIR, f"CAMPAIGN_{today}")
    os.makedirs(batch_dir, exist_ok=True)

    print("=" * 65)
    print(f"🚀 УПАКОВКА СОЦИАЛЬНЫХ КАМПАНИЙ В: {batch_dir}")
    print("=" * 65)

    # 1. Copy visuals
    if os.path.exists(VISUALS_DIR):
        img_dest = os.path.join(batch_dir, "visuals")
        os.makedirs(img_dest, exist_ok=True)
        for img in os.listdir(VISUALS_DIR):
            s = os.path.join(VISUALS_DIR, img)
            d = os.path.join(img_dest, img)
            shutil.copy2(s, d)
            print(f"  ✓ Графика скопирована: {img}")

    # 2. Copy campaign pack markdown
    src_pack = os.path.join(ROOT_DIR, "05_Content", "Posts", "LAUNCH_CAMPAIGN_PACK.md")
    if os.path.exists(src_pack):
        shutil.copy2(src_pack, os.path.join(batch_dir, "LAUNCH_CAMPAIGN_PACK.md"))
        print("  ✓ Сценарии и тексты постов скопированы.")

    # 3. Create ready Quick-Post file
    quick_file = os.path.join(batch_dir, "QUICK_PUBLISH_GUIDE.txt")
    with open(quick_file, "w", encoding="utf-8") as f:
        f.write(f"""======================================================================
ИНСТРУКЦИЯ ПО ПУБЛИКАЦИИ: КАМПАНИЯ {today}
======================================================================
1. INSTAGRAM:
   - Картинка: visuals/saas_vs_sovereign.jpg
   - Текст: См. Пост 2 в LAUNCH_CAMPAIGN_PACK.md
   - Ссылка в профиле: https://teleportviktor-debug.github.io/Rozario_Backup/sovereign_transformation.html

2. LINKEDIN:
   - Картинка: visuals/sovereign_architecture.jpg
   - Текст: См. Пост 1 в LAUNCH_CAMPAIGN_PACK.md
   - Призыв: Написать в ЛС для получения интерактивного ROI

3. TELEGRAM:
   - Картинка: visuals/ai_swarm_agents.jpg
   - Текст: См. Пост 3 в LAUNCH_CAMPAIGN_PACK.md
   - Кнопка: https://teleportviktor-debug.github.io/Rozario_Backup/client_presentation.html
======================================================================
""")
    print(f"  ✓ Сформирован гайд быстрой публикации: {quick_file}")
    print("\n🎉 ВСЕ МАТЕРИАЛЫ УСПЕШНО УПАКОВАНЫ И ГОТОВЫ К ПУБЛИКАЦИИ!")
    return batch_dir

if __name__ == "__main__":
    package_social_campaign()
