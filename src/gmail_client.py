import base64
import os
from email.utils import parsedate_to_datetime

from googleapiclient.discovery import build

from src.google_auth import get_google_credentials
from src.integrations_models import GmailMessage


def _decode(data: str | None) -> str:
    if not data:
        return ""

    return base64.urlsafe_b64decode(data).decode(
        "utf-8",
        errors="replace",
    )


def _get_headers(payload: dict) -> dict[str, str]:
    return {
        header["name"].lower(): header.get("value", "")
        for header in payload.get("headers", [])
    }


def _get_text(payload: dict) -> str:
    if payload.get("mimeType") == "text/plain":
        return _decode(payload.get("body", {}).get("data"))

    for part in payload.get("parts", []):
        text = _get_text(part)
        if text.strip():
            return text

    if payload.get("mimeType") == "text/html":
        return _decode(payload.get("body", {}).get("data"))

    return ""


def _get_created_at(headers: dict[str, str]) -> str | None:
    value = headers.get("date")

    if not value:
        return None

    try:
        return parsedate_to_datetime(value).isoformat()
    except (TypeError, ValueError, OverflowError):
        return None


def get_gmail_service():
    return build(
        "gmail",
        "v1",
        credentials=get_google_credentials(),
    )


def list_recent_messages(
    max_results: int | None = None,
) -> list[GmailMessage]:
    service = get_gmail_service()

    max_results = max_results or int(
        os.getenv("GMAIL_MAX_MESSAGES", "25")
    )

    response = (
        service.users()
        .messages()
        .list(
            userId="me",
            maxResults=max_results,
            q="newer_than:30d",
        )
        .execute()
    )

    messages = []

    for item in response.get("messages", []):
        message_id = item["id"]

        raw = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="full",
            )
            .execute()
        )

        payload = raw.get("payload", {})
        headers = _get_headers(payload)

        messages.append(
            GmailMessage(
                item_id=message_id,
                thread_id=raw.get("threadId"),
                sender=headers.get("from", ""),
                recipients=headers.get("to", ""),
                subject=headers.get("subject", ""),
                content=_get_text(payload).strip(),
                created_at=_get_created_at(headers),
                web_url=(
                    "https://mail.google.com/mail/u/0/"
                    f"#all/{message_id}"
                ),
            )
        )

    return messages
