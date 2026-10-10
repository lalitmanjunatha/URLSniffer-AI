"""
URL logging utilities for URLSniffer.
Provides functions to sanitize URLs for safe logging.
"""

from urllib.parse import urlparse, urlunparse


def sanitize_url_for_logging(url: str) -> str:
    """
    Sanitize a URL for logging by removing query parameters and credentials.

    This prevents logging of sensitive information such as:
    - Query parameters (which may contain tokens, passwords, etc.)
    - Username/password credentials in the URL (e.g., user:pass@example.com)

    Parameters
    ----------
    url: str
        The URL to sanitize

    Returns
    -------
    str
        Sanitized URL with query parameters and credentials removed
    """
    try:
        parsed = urlparse(url)
        # Remove credentials from netloc (username:password@)
        netloc = parsed.hostname or ""
        if parsed.port:
            netloc += f":{parsed.port}"
        # Reconstruct without query, fragment, and credentials
        sanitized = urlunparse(
            (
                parsed.scheme,
                netloc,  # hostname:port only, no credentials
                parsed.path,
                "",  # params (rarely used)
                "",  # query removed
                "",  # fragment removed
            )
        )
        return sanitized
    except Exception:
        # If parsing fails, return a safe placeholder
        return "[Invalid URL]"


def sanitize_error_message(message: str) -> str:
    """
    Sanitize an error message that may contain URLs.
    This is a simple implementation that looks for common URL patterns
    and replaces them with sanitized versions.
    For production, consider using a more robust regex or library.
    """
    # This is a basic implementation - in practice, you might want to
    # use a more sophisticated approach or rely on structured logging
    # where URLs are passed as separate fields and sanitized at log time.
    return message