from fastapi import Request


def extract_ip(request: Request) -> str | None:
    if request.client:
        return request.client.host
    return None
