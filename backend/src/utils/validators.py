"""
Input validation helpers.
"""
import re


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
