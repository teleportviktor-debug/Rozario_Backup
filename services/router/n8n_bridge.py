"""
n8n Bridge Webhook Module
Architecture "Genome" (Phase 1) - Razum Google AI PRO.

Integrates with n8n workflows under Zero Trust architecture:
- Authorizes via internal token matching `ntn_...` specification.
- Dispatches and receives Google Workspace CardService JSON payloads.
- Validates headers and incoming webhooks.
"""

import os
import json
import logging
import httpx
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from config.genome_config import settings
from services.schemas.card_service import GoogleWorkspaceCardMessage

logger = logging.getLogger("GenomeN8NBridge")


class N8NWebhookPayload(BaseModel):
    event: str = "workspace_card_generated"
    card_message: GoogleWorkspaceCardMessage
    metadata: Dict[str, Any] = Field(default_factory=dict)


class N8NBridge:
    """
    Zero-Trust n8n Webhook Connector.
    Ensures all outbound and inbound communication requires valid `ntn_...` token.
    """

    AUTH_HEADER_NAME = "X-N8N-Integration-Token"

    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.N8N_WEBHOOK_TOKEN
        self._validate_token_format(self.token)

    @classmethod
    def _validate_token_format(cls, token: str) -> None:
        """Validates token follows internal integration convention starting with 'ntn_'."""
        if not token or not token.startswith("ntn_"):
            raise ValueError(
                f"Invalid n8n integration token format. Must start with 'ntn_'. Received: '{token[:6]}...'"
            )

    def get_auth_headers(self) -> Dict[str, str]:
        """Returns required Zero-Trust headers for n8n API calls."""
        return {
            self.AUTH_HEADER_NAME: self.token,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "X-Genome-System": "Razum-Google-AI-PRO"
        }

    def verify_inbound_request(self, headers: Dict[str, str]) -> bool:
        """
        Validates inbound webhook from n8n ensuring secret token matches.
        Supports case-insensitive header lookup.
        """
        lower_headers = {k.lower(): v for k, v in headers.items()}
        inbound_token = (
            lower_headers.get(self.AUTH_HEADER_NAME.lower()) or
            lower_headers.get("x-n8n-token") or
            lower_headers.get("authorization", "").replace("Bearer ", "").strip()
        )

        if not inbound_token:
            logger.warning("Zero-Trust Rejection: Missing n8n authentication token in headers.")
            return False

        if inbound_token != self.token:
            logger.warning("Zero-Trust Rejection: Inbound n8n token mismatch.")
            return False

        return True

    async def dispatch_card_to_n8n(
        self,
        webhook_url: str,
        card_message: GoogleWorkspaceCardMessage,
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Asynchronously sends validated CardService JSON to an n8n webhook endpoint.
        """
        payload = N8NWebhookPayload(
            card_message=card_message,
            metadata=extra_metadata or {}
        )

        headers = self.get_auth_headers()
        json_body = payload.model_dump(mode="json", exclude_none=True)

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(webhook_url, json=json_body, headers=headers)
                response.raise_for_status()
                return {
                    "status": "DELIVERED",
                    "status_code": response.status_code,
                    "response": response.text[:200]
                }
            except httpx.HTTPError as err:
                logger.error(f"n8n webhook dispatch error: {err}")
                return {
                    "status": "FAILED",
                    "error": str(err)
                }
