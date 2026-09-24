import ipaddress
import socket
from urllib.parse import urljoin, urlparse

from .config import settings


class TargetError(ValueError):
    """Raised when a target is outside the configured authorized scope."""


def validate_target(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise TargetError("target must use http or https and include a hostname")
    if parsed.username or parsed.password:
        raise TargetError("credentials in target URLs are not allowed")
    if parsed.fragment:
        raise TargetError("URL fragments are not sent to servers")
    host = parsed.hostname.rstrip(".").lower()
    if host in {"localhost", "localhost.localdomain"}:
        allowed = True
    else:
        try:
            addresses = {ipaddress.ip_address(host)}
        except ValueError:
            try:
                addresses = {ipaddress.ip_address(item[4][0]) for item in socket.getaddrinfo(host, parsed.port or 80)}
            except OSError as exc:
                raise TargetError("target hostname cannot be resolved") from exc
        allowed = all(not (address.is_private or address.is_loopback or address.is_link_local or address.is_reserved) for address in addresses)
    if not settings.allow_private_targets and not allowed:
        raise TargetError("private and loopback targets are disabled by policy")
    return parsed._replace(fragment="").geturl().rstrip("/")


def safe_url(base: str, path: str) -> str:
    if not path.startswith("/") or path.startswith("//"):
        raise TargetError("discovered paths must be absolute and relative to the target")
    candidate = urljoin(base.rstrip("/") + "/", path.lstrip("/"))
    if urlparse(candidate).netloc != urlparse(base).netloc:
        raise TargetError("redirected or cross-origin URL rejected")
    return candidate
