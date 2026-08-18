"""
Input validation helpers.
"""
import ipaddress
import socket
import re
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """Check if a string is a valid URL."""
    pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$',
        re.IGNORECASE,
    )
    return bool(pattern.match(url))


def sanitize_text(text: str, max_length: int = 10000) -> str:
    """Sanitize input text."""
    if len(text) > max_length:
        return text[:max_length]
    return text.strip()


def is_safe_url_for_scraping(url: str) -> bool:
    """
    SSRF guard for user-supplied scrape URLs.

    Allows only http/https URLs whose hostname resolves to public addresses.
    Rejects loopback, private, link-local, reserved, multicast and unreachable
    ranges (including Docker/localhost addresses) so the server cannot be used
    to probe internal services.
    """
    try:
        parsed = urlparse(url)
    except (ValueError, TypeError):
        return False

    if parsed.scheme not in ("http", "https"):
        return False

    hostname = (parsed.hostname or "").strip().lower()
    if not hostname:
        return False

    # Direct IP literal
    try:
        ip = ipaddress.ip_address(hostname)
        return _is_public_ip(ip)
    except ValueError:
        pass

    # Hostname: resolve and check every resulting address
    try:
        infos = socket.getaddrinfo(hostname, parsed.port or (443 if parsed.scheme == "https" else 80),
                                   proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        return False

    if not infos:
        return False

    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if not _is_public_ip(ip):
            return False
    return True


def _is_public_ip(ip: "ipaddress.IPv4Address | ipaddress.IPv6Address") -> bool:
    return (
        not ip.is_private
        and not ip.is_loopback
        and not ip.is_link_local
        and not ip.is_reserved
        and not ip.is_multicast
        and not ip.is_unspecified
    )
