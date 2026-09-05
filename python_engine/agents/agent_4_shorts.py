"""
============================================================================
AGENT 4: 15s SHORTS VIDEO SCRIPTING & RENDERING PIPELINE ENGINE
High Retention Hook Scripts (180 WPM) + MoviePy / FFmpeg Cloud Command Pipeline
============================================================================
"""

import os
import json
from datetime import datetime

def generate_15s_shorts():
    shorts = [
        {
            "id": "SHORT-15S-01",
            "title": "Секрет 1 дубля: Как записать видео без запинок",
            "duration_sec": 15,
            "target_words": 42,
            "tempo_wpm": 180,
            "hook_0_3s": "Перестаньте перезаписывать ролики по 20 раз!",
            "body_3_12s": "Секрет в AI Media Studio: ровно 15 слов на 5 секунд. Загружаете текст, и нейросеть генерирует видео в идеальном ритме.",
            "cta_12_15s": "Жми ссылку в шапке, чтобы открыть AI Media Studio!",
            "full_speech_script": (
                "Перестаньте перезаписывать ролики по 20 раз! [ПАУЗА 0.3s] "
                "Секрет в AI Media Studio: ровно 15 слов на 5 секунд. [ПАУЗА] "
                "Загружаете текст, и нейросеть генерирует видео в идеальном ритме. "
                "Жми ссылку в шапке, чтобы открыть AI Media Studio!"
            ),
            "ffmpeg_pipeline": {
                "input_video": "raw_takes/speaker_take_01.webm",
                "bg_audio": "audio/lofi_flow_84bpm.mp3",
                "resolution": "1080x1920",
                "fps": 30,
                "command": (
                    "ffmpeg -y -i raw_takes/speaker_take_01.webm -i audio/lofi_flow_84bpm.mp3 "
                    "-filter_complex \"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[v];"
                    "[1:a]volume=0.15[bg];[0:a][bg]amix=inputs=2:duration=first[a]\" "
                    "-map \"[v]\" -map \"[a]\" -c:v libx264 -preset fast -crf 22 -c:a aac -b:a 192k "
                    "output/short_15s_01_rendered.mp4"
                )
            }
        },
        {
            "id": "SHORT-15S-02",
            "title": "Как ИИ находит клиентов на $1,500 за 48 часов",
            "duration_sec": 15,
            "target_words": 40,
            "tempo_wpm": 180,
            "hook_0_3s": "Хватит делать холодные рассылки вслепую.",
            "body_3_12s": "Наш автономный агент сам сканирует сайты конкурентов, находит 5 критических ошибок и формирует персональное видео за 30 секунд.",
            "cta_12_15s": "Попробуй тестовый аудит прямо сейчас — ссылка в профиле.",
            "full_speech_script": (
                "Хватит делать холодные рассылки вслепую. [ПАУЗА 0.3s] "
                "Наш автономный агент сам сканирует сайты конкурентов, находит 5 критических ошибок и формирует персональное видео за 30 секунд. "
                "Попробуй тестовый аудит прямо сейчас — ссылка в профиле."
            ),
            "ffmpeg_pipeline": {
                "input_video": "raw_takes/speaker_take_02.webm",
                "bg_audio": "audio/lofi_flow_84bpm.mp3",
                "resolution": "1080x1920",
                "fps": 30,
                "command": (
                    "ffmpeg -y -i raw_takes/speaker_take_02.webm -i audio/lofi_flow_84bpm.mp3 "
                    "-filter_complex \"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[v];"
                    "[1:a]volume=0.15[bg];[0:a][bg]amix=inputs=2:duration=first[a]\" "
                    "-map \"[v]\" -map \"[a]\" -c:v libx264 -preset fast -crf 22 -c:a aac -b:a 192k "
                    "output/short_15s_02_rendered.mp4"
                )
            }
        }
    ]
    return shorts

def run_shorts_agent(output_dir=None):
    if output_dir is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_dir = os.path.join(root_dir, "05_CONTENT_PRODUCTION", "Shorts")
        if not os.path.exists(output_dir):
            output_dir = os.path.join(root_dir, "05_Content", "Shorts")

    os.makedirs(output_dir, exist_ok=True)

    shorts = generate_15s_shorts()

    # Save JSON batch
    json_path = os.path.join(output_dir, "shorts_scripts_batch.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"agent": "agent_4_shorts", "generated_at": datetime.now().isoformat(), "shorts": shorts}, f, ensure_ascii=False, indent=2)

    # Save Shell Render Manifest
    sh_path = os.path.join(output_dir, "ffmpeg_render_manifest.sh")
    with open(sh_path, "w", encoding="utf-8") as f:
        f.write("#!/bin/bash\n# FFmpeg MoviePy Cloud Rendering Batch for 15s Shorts\n\n")
        for s in shorts:
            f.write(f"# --- {s['id']}: {s['title']} ---\n")
            f.write(f"echo 'Rendering {s['id']}...'\n")
            f.write(f"{s['ffmpeg_pipeline']['command']}\n\n")

    return {
        "status": "SUCCESS",
        "agent_id": "agent_4_shorts",
        "shorts_created": len(shorts),
        "json_output": json_path,
        "sh_output": sh_path
    }

if __name__ == "__main__":
    res = run_shorts_agent()
    print(f"✓ [agent_4_shorts] Created {res['shorts_created']} 15s shorts scripts. Manifest: {res['sh_output']}")
