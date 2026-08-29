from pathlib import Path
import os

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar",
]


def get_google_credentials() -> Credentials:
    token_path = Path(os.getenv("GOOGLE_TOKEN_FILE", "token.json"))
    credentials_path = Path(
        os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    )

    credentials = None

    if token_path.exists():
        credentials = Credentials.from_authorized_user_file(
            str(token_path),
            SCOPES,
        )

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    if not credentials or not credentials.valid:
        if not credentials_path.exists():
            raise FileNotFoundError(
                f"Missing Google credentials file: {credentials_path}"
            )

        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_path),
            SCOPES,
        )

        credentials = flow.run_local_server(
            port=0,
            access_type="offline",
            prompt="consent",
        )

    token_path.write_text(
        credentials.to_json(),
        encoding="utf-8",
    )

    return credentials
