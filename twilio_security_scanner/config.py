import os
import dotenv
from typing import Tuple


def load_config() -> Tuple[str, str]:
    """
    Load and validate Twilio configuration from environment variables.
    Supports both AuthToken and API Key authentication.

    Returns:
        Tuple[str, str]: A tuple containing either:
            - (account_sid, auth_token) for AuthToken auth
            - (api_key_sid, api_key_secret) for API Key auth

    Raises:
        ValueError: If required environment variables are missing
    """
    dotenv.load_dotenv()

    # Check for Account SID first as it's required for all auth methods
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    if not account_sid:
        raise ValueError(
            "Missing TWILIO_ACCOUNT_SID. This is required for all authentication methods."
        )

    # Try API Key authentication first
    api_key_sid = os.getenv("TWILIO_API_KEY_SID")
    api_key_secret = os.getenv("TWILIO_API_KEY_SECRET")

    if api_key_sid and api_key_secret:
        return api_key_sid, api_key_secret

    # Fall back to Auth Token authentication
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    if not auth_token:
        raise ValueError(
            "Missing authentication credentials. Please provide either:\n"
            "1. API Key authentication:\n"
            "   - TWILIO_API_KEY_SID\n"
            "   - TWILIO_API_KEY_SECRET\n"
            "2. Auth Token authentication:\n"
            "   - TWILIO_AUTH_TOKEN"
        )

    return account_sid, auth_token
