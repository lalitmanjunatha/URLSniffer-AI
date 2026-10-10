"""URL validation utilities for URLSniffer.

This module provides a strict URL validator that checks the syntax of a URL
without making any network calls. It ensures the URL has a valid scheme (http/https)
and a valid hostname (domain or IPv4 address). It does not validate that the
host actually exists or is reachable.

The validator is intentionally strict to prevent obviously malformed URLs from
reaching the feature extraction and ML pipeline.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

# Regular expression for validating domain names (simplified).
# This allows letters, digits, hyphens, and dots, but not starting or ending with hyphen or dot.
_DOMAIN_LABEL_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", re.IGNORECASE)

# Regular expression for IPv4 addresses.
_IPV4_RE = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")


def _is_valid_ipv4(host: str) -> bool:
    """Return True if host is a valid IPv4 address."""
    if not _IPV4_RE.match(host):
        return False
    parts = host.split(".")
    for part in parts:
        if int(part) > 255:
            return False
    return True


def _is_valid_domain(host: str) -> bool:
    """Return True if host is a valid domain name.

    A domain consists of labels separated by dots. Each label must:
    - Contain only letters, digits, hyphens.
    - Not start or end with a hyphen.
    - Not be empty.
    The TLD must be at least two letters (we don't validate the TLD list).
    """
    if not host or host.startswith(".") or host.endswith("."):
        return False
    labels = host.split(".")
    if len(labels) < 2:
        # At least domain and TLD
        return False
    for label in labels:
        if not label:
            return False
        if label.startswith("-") or label.endswith("-"):
            return False
        if not _DOMAIN_LABEL_RE.match(label):
            return False
    # Additional check: TLD should be all letters (simplified)
    tld = labels[-1]
    if not tld.isalpha():
        return False
    return True


def is_valid_url(url: str) -> bool:
    """Validate a URL string.

    Parameters
    ----------
    url: str
        The URL to validate.

    Returns
    -------
    bool
        True if the URL has a valid scheme (http/https) and a valid hostname
        (domain or IPv4 address), False otherwise.

    Notes
    -----
    This function does NOT:
    - Check if the URL is reachable.
    - Validate port numbers (though they must be numeric if present).
    - Validate query strings or fragments beyond ensuring they don't contain
      invalid characters (urlparse handles this).
    - Perform any network calls.
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return False

    # Scheme must be http or https
    if parsed.scheme not in ("http", "https"):
        return False

    # Hostname must be present
    host = parsed.hostname
    if not host:
        return False

    # Hostname must be either a valid IPv4 address or a valid domain
    if _is_valid_ipv4(host):
        return True
    if _is_valid_domain(host):
        return True

    return False