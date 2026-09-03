"""
============================================================================
GOOGLE DRIVE TO MARKDOWN CONVERTER MICROSERVICE (main.py)
Autonomous File Ingestion, Parsing & Pipeline Dispatcher
Compatible with: CLI • 24/7 Daemon • Google Cloud Functions • Railway • VM
============================================================================
"""

import os
import sys
import time
import shutil
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, List

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from config import (
    TEMP_DIR, POLL_INTERVAL_SECONDS, BATCH_SIZE_LIMIT, SUPPORTED_EXTENSIONS
)
from drive_service import GoogleDriveService
from converter import DocumentConverterEngine

# Configure Logging with UTF-8
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
logger = logging.getLogger("DriveMarkdownConverter")
logger.setLevel(logging.INFO)
logger.handlers = [handler]

class DriveMarkdownPipeline:
    def __init__(self):
        logger.info("Initializing Drive Markdown Pipeline...")
        self.drive = GoogleDriveService()
        self.converter = DocumentConverterEngine(prefer_engine="markitdown")
        os.makedirs(TEMP_DIR, exist_ok=True)

    def process_single_file(self, file_meta: Dict[str, Any]) -> bool:
        """
        Processes a single file: Download -> Convert -> Upload MD -> Move to Archive.
        """
        file_id = file_meta.get("id")
        file_name = file_meta.get("name")
        mime_type = file_meta.get("mimeType")

        ext = Path(file_name).suffix.lower()
        if not ext and mime_type.startswith("application/vnd.google-apps"):
            ext = ".gdoc"

        logger.info(f"\n[Processing] {file_name} (ID: {file_id})")

        local_temp_file = os.path.join(TEMP_DIR, f"{file_id}_{file_name}")

        try:
            # 1. Download / Export from Google Drive
            downloaded_path = self.drive.download_file(file_id, file_name, mime_type, local_temp_file)
            logger.info(f"  -> Downloaded to temp storage: {downloaded_path}")

            # 2. Convert to Clean Structured Markdown
            conv_result = self.converter.convert_to_markdown(downloaded_path, file_name)
            md_content = conv_result["markdown"]
            logger.info(f"  -> Converted ({conv_result['engine']}): {conv_result['word_count']} words, {conv_result['char_count']} chars.")

            # 3. Upload .md to 02_FOR_NOTEBOOK
            md_filename = f"{Path(file_name).stem}.md"
            uploaded_id = self.drive.upload_markdown(md_filename, md_content)
            logger.info(f"  -> Saved to 02_FOR_NOTEBOOK: {md_filename} (ID: {uploaded_id})")

            # 4. Move Original File to _ARCHIVE
            self.drive.move_to_archive(file_id)
            logger.info(f"  -> Moved source file to _ARCHIVE.")

            return True

        except Exception as e:
            logger.error(f"  [ERROR] Processing file {file_name}: {e}", exc_info=True)
            return False

        finally:
            # Cleanup local temp file
            if os.path.exists(local_temp_file):
                try:
                    os.remove(local_temp_file)
                except Exception:
                    pass

    def run_pipeline_batch(self) -> Dict[str, Any]:
        """
        Scans 01_INBOX and processes a batch of files.
        """
        inbox_files = self.drive.list_inbox_files(limit=BATCH_SIZE_LIMIT)
        if not inbox_files:
            logger.info("[STATUS] 01_INBOX is empty. No files to process.")
            return {"processed": 0, "failed": 0, "total": 0}

        logger.info(f"[INBOX] Found {len(inbox_files)} files in 01_INBOX.")

        processed_count = 0
        failed_count = 0

        for f in inbox_files:
            success = self.process_single_file(f)
            if success:
                processed_count += 1
            else:
                failed_count += 1

        logger.info(f"[DONE] Batch complete. Processed: {processed_count}, Failed: {failed_count}")
        return {
            "processed": processed_count,
            "failed": failed_count,
            "total": len(inbox_files)
        }

    def run_daemon_loop(self):
        """
        Continuous polling daemon loop with auto-reconnect & exponential backoff.
        Automatically recovers from network drops (WinError 10053, timeouts, etc.)
        """
        logger.info(f"[DAEMON] Starting 24/7 Daemon mode. Polling interval: {POLL_INTERVAL_SECONDS}s")
        consecutive_errors = 0
        max_backoff = 300  # max 5 minutes between retries

        while True:
            try:
                self.run_pipeline_batch()
                consecutive_errors = 0  # reset on success
                time.sleep(POLL_INTERVAL_SECONDS)

            except KeyboardInterrupt:
                logger.info("[DAEMON] Stopped by user (Ctrl+C).")
                break

            except Exception as e:
                consecutive_errors += 1
                backoff = min(POLL_INTERVAL_SECONDS * (2 ** (consecutive_errors - 1)), max_backoff)
                logger.warning(
                    f"[DAEMON] Network error (attempt {consecutive_errors}): {type(e).__name__}: {e}"
                )
                logger.info(f"[DAEMON] Auto-reconnect in {backoff}s... (reinitializing Drive client)")
                time.sleep(backoff)
                try:
                    # Reinitialize the Drive connection after network error
                    from drive_service import GoogleDriveService
                    self.drive = GoogleDriveService()
                    logger.info("[DAEMON] Drive client reinitialized successfully.")
                except Exception as reconnect_err:
                    logger.error(f"[DAEMON] Reconnect failed: {reconnect_err}")

def cloud_function_http(request):
    pipeline = DriveMarkdownPipeline()
    result = pipeline.run_pipeline_batch()
    return (result, 200, {"Content-Type": "application/json"})

def cloud_function_pubsub(event, context):
    pipeline = DriveMarkdownPipeline()
    return pipeline.run_pipeline_batch()

def main():
    parser = argparse.ArgumentParser(description="Google Drive to Markdown Converter Microservice")
    parser.add_argument("--daemon", action="store_true", help="Run in continuous polling daemon mode")
    parser.add_argument("--once", action="store_true", help="Run once for current 01_INBOX and exit")
    args = parser.parse_args()

    pipeline = DriveMarkdownPipeline()

    if args.daemon:
        pipeline.run_daemon_loop()
    else:
        pipeline.run_pipeline_batch()

if __name__ == "__main__":
    main()
