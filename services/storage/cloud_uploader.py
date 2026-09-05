import os
import sys
import json
from pathlib import Path
from google.cloud import storage
from google.api_core.exceptions import NotFound, Forbidden, Conflict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SERVICE_ACCOUNT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "service_account.json")
)

def get_service_account_info() -> dict:
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        raise FileNotFoundError(f"service_account.json not found at: {SERVICE_ACCOUNT_PATH}")
    with open(SERVICE_ACCOUNT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_storage_client() -> storage.Client:
    sa_info = get_service_account_info()
    project_id = sa_info.get("project_id", "gen-lang-client-0207478259")
    return storage.Client.from_service_account_json(SERVICE_ACCOUNT_PATH, project=project_id)

def get_default_bucket_name() -> str:
    sa_info = get_service_account_info()
    project_id = sa_info.get("project_id", "gen-lang-client-0207478259")
    # Clean project_id for bucket naming (only lowercase, digits, hyphens)
    clean_id = project_id.lower().replace("_", "-")
    return f"outreach-audit-vault-{clean_id}"

def ensure_bucket_public(bucket: storage.Bucket) -> None:
    """Configures bucket or objects to be publicly readable by allUsers."""
    try:
        # 1. Try uniform bucket-level IAM policy
        policy = bucket.get_iam_policy(requested_policy_version=3)
        has_viewer = any(
            b.get("role") == "roles/storage.objectViewer" and "allUsers" in b.get("members", [])
            for b in policy.bindings
        )
        if not has_viewer:
            policy.bindings.append({
                "role": "roles/storage.objectViewer",
                "members": {"allUsers"}
            })
            bucket.set_iam_policy(policy)
            print(f"🔓 [GCS] Бакет '{bucket.name}' настроен с публичным доступом (roles/storage.objectViewer -> allUsers)")
    except Exception as e:
        # If uniform bucket-level access is disabled, individual object ACLs will be used
        print(f"ℹ️ [GCS IAM Policy Notice]: {e}")

def get_or_create_bucket(bucket_name: str = None) -> storage.Bucket:
    """Returns existing bucket or creates a new one with public read access."""
    client = get_storage_client()
    if not bucket_name:
        bucket_name = get_default_bucket_name()

    try:
        bucket = client.get_bucket(bucket_name)
        print(f"📦 [GCS] Найден существующий бакет: '{bucket.name}'")
        ensure_bucket_public(bucket)
        return bucket
    except NotFound:
        print(f"🚀 [GCS] Бакет '{bucket_name}' не найден. Создание нового бакета в локации US...")
        try:
            bucket = client.create_bucket(bucket_name, location="US")
            print(f"✅ [GCS] Бакет '{bucket.name}' успешно создан!")
            ensure_bucket_public(bucket)
            return bucket
        except Forbidden as fe:
            sa_info = get_service_account_info()
            email = sa_info.get("client_email")
            project = sa_info.get("project_id")
            error_msg = (
                f"\n❌ [ОШИБКА ДОСТУПА GCS 403 FORBIDDEN]:\n"
                f"Сервисный аккаунт '{email}' не имеет роли 'Storage Admin' в проекте '{project}'.\n\n"
                f"Чтобы разрешить создание и управление бакетами:\n"
                f"1. Перейдите в Google Cloud Console IAM:\n"
                f"   https://console.cloud.google.com/iam-admin/iam?project={project}\n"
                f"2. Найдите аккаунт: {email}\n"
                f"3. Нажмите 'Изменить' (карандаш) -> 'Добавить другую роль' -> выберите 'Администратор Storage' (Storage Admin).\n"
                f"4. Сохраните изменения."
            )
            raise PermissionError(error_msg) from fe

def upload_video_to_cloud(local_file_path: str, bucket_name: str = None) -> str:
    """
    Uploads a local MP4 video to Google Cloud Storage and returns a permanent public URL.
    
    Args:
        local_file_path: Absolute or relative path to the local video file.
        bucket_name: Optional custom bucket name (defaults to outreach-audit-vault-<project_id>).
        
    Returns:
        Permanent public URL: https://storage.googleapis.com/<bucket_name>/<filename>.mp4
    """
    if not os.path.exists(local_file_path):
        raise FileNotFoundError(f"Local video file does not exist: {local_file_path}")

    bucket = get_or_create_bucket(bucket_name)
    blob_name = os.path.basename(local_file_path)
    blob = bucket.blob(blob_name)

    print(f"📤 [GCS UPLOAD] Загрузка видео: '{blob_name}' -> gs://{bucket.name}/{blob_name}...")
    blob.upload_from_filename(local_file_path, content_type="video/mp4")
    print(f"✅ [GCS UPLOAD] Загрузка завершена: {blob.size} байт")

    # Ensure individual object is public (if fine-grained ACLs are used)
    try:
        blob.make_public()
    except Exception:
        pass

    public_url = f"https://storage.googleapis.com/{bucket.name}/{blob_name}"
    print(f"🌐 [GCS PUBLIC URL] {public_url}")
    return public_url

if __name__ == "__main__":
    print(f"Using service account: {SERVICE_ACCOUNT_PATH}")
    info = get_service_account_info()
    print(f"Project ID: {info.get('project_id')}")
    print(f"Client Email: {info.get('client_email')}")
    print(f"Default Bucket: {get_default_bucket_name()}")
