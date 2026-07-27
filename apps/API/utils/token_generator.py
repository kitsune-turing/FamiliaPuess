import secrets


def generate_token_value() -> str:
    return secrets.token_urlsafe(32)
