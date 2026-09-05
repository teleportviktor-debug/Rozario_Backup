import os
import sys
import glob
import urllib.request
import urllib.error

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.storage.cloud_uploader import upload_video_to_cloud

def find_test_video() -> str:
    # Prefer Tesoro.help outreach video
    pattern = os.path.join("output", "rendered_videos", "outreach_tesoro_help_*.mp4")
    matches = glob.glob(pattern)
    if matches:
        return os.path.abspath(matches[0])
    
    # Any other mp4 in output/rendered_videos
    all_videos = glob.glob(os.path.join("output", "rendered_videos", "*.mp4"))
    if all_videos:
        return os.path.abspath(all_videos[0])
    
    raise FileNotFoundError("No rendered MP4 videos found in output/rendered_videos/")

def verify_public_url(url: str) -> bool:
    print("\n" + "=" * 76)
    print("🕵️ [VERIFY PUBLIC GCS URL] Тестирование публичного доступа...")
    print(f"   Целевой URL: {url}")
    print("=" * 76)

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            status = resp.status
            content_type = resp.headers.get("Content-Type", "")
            content_length = resp.headers.get("Content-Length", "unknown")

            print(f"\n[ТЕСТ 1/2] HTTP Статус ответа:")
            print(f"  Статус: {status}")
            if status == 200:
                print("  ✅ [PASS]: Получен статус 200 OK без авторизации.")
            else:
                print(f"  ❌ [FAIL]: Ожидался статус 200, получен {status}")
                return False

            print(f"\n[ТЕСТ 2/2] Content-Type и размер:")
            print(f"  Content-Type: {content_type}")
            print(f"  Content-Length: {content_length} байт")
            if "video/mp4" in content_type:
                print("  ✅ [PASS]: Content-Type соответствует 'video/mp4'.")
            else:
                print(f"  ❌ [FAIL]: Неверный Content-Type '{content_type}'")
                return False

            print("\n" + "=" * 76)
            print("🏆 [РЕЗУЛЬТАТ АУДИТА: 100% УСПЕХ]")
            print(f"   Видео доступно всему миру: {url}")
            print("=" * 76)
            return True
    except urllib.error.HTTPError as e:
        print(f"\n❌ [HTTP ERROR]: {e.code} {e.reason}")
        if e.code == 403:
            print("   Доступ к объекту запрещен (Access Denied). Бакет или объект не публичен.")
        elif e.code == 404:
            print("   Объект не найден в бакете.")
        return False
    except Exception as ex:
        print(f"\n❌ [NETWORK ERROR]: {ex}")
        return False

def main():
    try:
        video_path = find_test_video()
        print(f"🎬 Тестовый видеофайл: {video_path} ({os.path.getsize(video_path)} байт)")
        public_url = upload_video_to_cloud(video_path)
        success = verify_public_url(public_url)
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка выполнения теста: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
