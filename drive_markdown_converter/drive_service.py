"""
============================================================================
GOOGLE DRIVE API SERVICE WRAPPER (drive_service.py)
Encapsulates Authentication, Search, Download, Upload & Folder Relocation
============================================================================
"""

import io
import os
import sys
import logging
from typing import List, Dict, Any, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload, MediaInMemoryUpload
from googleapiclient.errors import HttpError

from config import (
    get_service_account_credentials_dict,
    INBOX_FOLDER_NAME, NOTEBOOK_FOLDER_NAME, ARCHIVE_FOLDER_NAME,
    INBOX_FOLDER_ID, NOTEBOOK_FOLDER_ID, ARCHIVE_FOLDER_ID
)

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive"]

class GoogleDriveService:
    def __init__(self):
        self.service = self._init_drive_client()
        self.folder_ids = self._resolve_folders()

    def _init_drive_client(self):
        """Initializes Google Drive API v3 client using Service Account."""
        creds_dict = get_service_account_credentials_dict()
        if creds_dict:
            creds = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=SCOPES
            )
            logger.info("[AUTH] Authenticated successfully using Service Account credentials.")
        else:
            import google.auth
            creds, _ = google.auth.default(scopes=SCOPES)
            logger.info("[AUTH] Authenticated using Google Default Application Credentials.")

        return build("drive", "v3", credentials=creds, cache_discovery=False)

    def _resolve_folders(self) -> Dict[str, str]:
        """Resolves folder IDs for INBOX, NOTEBOOK, and ARCHIVE."""
        resolved = {}

        resolved["inbox"] = INBOX_FOLDER_ID or self._find_or_create_folder(INBOX_FOLDER_NAME)
        resolved["notebook"] = NOTEBOOK_FOLDER_ID or self._find_or_create_folder(NOTEBOOK_FOLDER_NAME)
        resolved["archive"] = ARCHIVE_FOLDER_ID or self._find_or_create_folder(ARCHIVE_FOLDER_NAME)

        logger.info(f"[FOLDERS] INBOX={resolved['inbox']}, NOTEBOOK={resolved['notebook']}, ARCHIVE={resolved['archive']}")
        return resolved

    def _find_or_create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> str:
        """Finds existing folder by name or creates a new one."""
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = self.service.files().list(
            q=query,
            spaces="drive",
            fields="files(id, name)",
            pageSize=1
        ).execute()

        files = results.get("files", [])
        if files:
            return files[0]["id"]

        metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder"
        }
        if parent_id:
            metadata["parents"] = [parent_id]

        folder = self.service.files().create(body=metadata, fields="id").execute()
        logger.info(f"[CREATE] Created folder: {folder_name} (ID: {folder.get('id')})")
        return folder.get("id")

    def list_inbox_files(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Lists unprocessed files in the 01_INBOX folder."""
        inbox_id = self.folder_ids["inbox"]
        query = f"'{inbox_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed = false"

        results = self.service.files().list(
            q=query,
            spaces="drive",
            fields="files(id, name, mimeType, size, modifiedTime, createdTime)",
            pageSize=limit,
            orderBy="createdTime asc"
        ).execute()

        return results.get("files", [])

    def download_file(self, file_id: str, file_name: str, mime_type: str, dest_path: str) -> str:
        """
        Downloads a binary file or exports Google Workspace Docs/Sheets to standard formats.
        """
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        if mime_type == "application/vnd.google-apps.document":
            request = self.service.files().export_media(
                fileId=file_id,
                mimeType="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            if not dest_path.endswith(".docx"):
                dest_path += ".docx"
        elif mime_type == "application/vnd.google-apps.spreadsheet":
            request = self.service.files().export_media(
                fileId=file_id,
                mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            if not dest_path.endswith(".xlsx"):
                dest_path += ".xlsx"
        elif mime_type == "application/vnd.google-apps.presentation":
            request = self.service.files().export_media(
                fileId=file_id,
                mimeType="application/pdf"
            )
            if not dest_path.endswith(".pdf"):
                dest_path += ".pdf"
        else:
            request = self.service.files().get_media(fileId=file_id)

        with io.FileIO(dest_path, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, request, chunksize=1024 * 1024 * 4)
            done = False
            while not done:
                status, done = downloader.next_chunk()

        return dest_path

    def upload_markdown(self, filename: str, content: str) -> str:
        """
        Uploads converted Markdown content to 02_FOR_NOTEBOOK folder.
        """
        notebook_id = self.folder_ids["notebook"]
        metadata = {
            "name": filename,
            "parents": [notebook_id],
            "mimeType": "text/markdown"
        }

        media = MediaInMemoryUpload(
            content.encode("utf-8"),
            mimetype="text/markdown",
            resumable=False
        )

        file = self.service.files().create(
            body=metadata,
            media_body=media,
            fields="id, name, webViewLink"
        ).execute()

        logger.info(f"[UPLOAD] Uploaded Markdown: {filename} (ID: {file.get('id')})")
        return file.get("id")

    def move_to_archive(self, file_id: str):
        """
        Moves the original source file from 01_INBOX to _ARCHIVE folder.
        """
        inbox_id = self.folder_ids["inbox"]
        archive_id = self.folder_ids["archive"]

        try:
            self.service.files().update(
                fileId=file_id,
                addParents=archive_id,
                removeParents=inbox_id,
                fields="id, parents"
            ).execute()
            logger.info(f"[ARCHIVE] Moved file {file_id} to _ARCHIVE folder.")
        except HttpError as e:
            logger.error(f"[ERROR] Failed to move file {file_id} to archive: {e}")
            raise
