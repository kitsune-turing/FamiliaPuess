import ipaddress

from fastapi import Request


def extract_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    elif request.client:
        ip = request.client.host
    else:
        return None
    try:
        ipaddress.ip_address(ip)
        return ip
    except ValueError:
        return None
