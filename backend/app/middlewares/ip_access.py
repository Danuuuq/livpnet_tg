import ipaddress
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

allowed_networks = [
    ipaddress.ip_network(ip) for ip in settings.ALLOWED_IP_YOOKASSA
]


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        ip_obj = ipaddress.ip_address(client_ip)

        if request.url.path.startswith('/subscription/yookassa'):
            if not any(ip_obj in network for network in allowed_networks):
                raise HTTPException(status_code=403, detail='Access denied')

        return await call_next(request)
