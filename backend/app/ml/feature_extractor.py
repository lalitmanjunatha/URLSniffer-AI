"""Feature extraction utilities for URLSniffer.

This module provides a deterministic extractor that turns a raw URL string
into a feature dictionary suitable for ML models. No network calls are made –
the logic is purely syntactic and operates on the URL string.

Feature set
=============
Original features (preserved for backward compatibility):
- ``url_length``: Total character count of the URL.
- ``scheme``: Binary flag indicating whether the scheme is HTTP/HTTPS.
- ``has_ip``: Binary flag if the host part is an IPv4 address.
- ``has_punycode``: Binary flag if any hostname component is a punycode label.
- ``percent_encoding``: Binary flag if the URL contains percent-encoded sequences.
- ``hyphen_count``: Total count of '-' characters in the host, path, query and fragment.
- ``digit_count``: Total count of digits in the entire URL.
- ``subdomain_count``: Number of sub‑domain components; netloc with two labels results in 0,
  three labels results in 1, etc.

New features added for improved detection:
- ``hostname_length``: Length of the hostname component.
- ``path_length``: Length of the path component.
- ``query_length``: Length of the query component.
- ``fragment_length``: Length of the fragment component.
- ``tld_length``: Length of the top-level domain (last label in hostname).
- ``hostname_dot_count``: Number of dots in the hostname.
- ``path_dot_count``: Number of dots in the path.
- ``query_param_count``: Number of query parameters (separated by &).
- ``has_at_sign``: Binary flag if URL contains @ (possible embedded credentials).
- ``tilde_count``: Total count of '~' characters.
- ``underscore_count``: Total count of '_' characters.
- ``colon_count``: Total count of ':' characters.
- ``semicolon_count``: Total count of ';' characters.
- ``bracket_count``: Total count of '[' and ']' characters.
- ``brace_count``: Total count of '{' and '}' characters.
- ``parenthesis_count``: Total count of '(' and ')' characters.
- ``single_quote_count``: Total count of ''' characters.
- ``double_quote_count``: Total count of '"' characters.
- ``backtick_count``: Total count of '`' characters.

Canonical feature order (must match the order in the return statement below):
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

# Regular expression to match IPv4 addresses.
_IPV4_RE = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")

# Regular expression to detect percent encoding.
_PERCENT_RE = re.compile(r"%[0-9A-Fa-f]{2}")

# Regular expression to detect punycode labels.
_PUNY_RE = re.compile(r"xn--")

FEATURE_NAMES = [
    "url_length",
    "scheme",
    "has_ip",
    "has_punycode",
    "percent_encoding",
    "hyphen_count",
    "digit_count",
    "subdomain_count",
    "hostname_length",
    "path_length",
    "query_length",
    "fragment_length",
    "tld_length",
    "hostname_dot_count",
    "path_dot_count",
    "query_param_count",
    "has_at_sign",
    "tilde_count",
    "underscore_count",
    "colon_count",
    "semicolon_count",
    "bracket_count",
    "brace_count",
    "parenthesis_count",
    "single_quote_count",
    "double_quote_count",
    "backtick_count",
]


def _is_ipv4(host: str) -> bool:
    """Return True if *host* is an IPv4 address.

    The function performs each octet numeric check to reject values > 255.
    """
    if not _IPV4_RE.match(host):
        return False
    parts = host.split(".")
    for part in parts:
        # Leading zeros are allowed but should not produce
        # ambiguous interpretations (e.g. "01" as 1)
        if not part.isdigit():
            return False
        num = int(part)
        if num < 0 or num > 255:
            return False
    return True


def _has_punycode(host: str) -> bool:
    """Return True if any hostname component is a punycode label."""
    return bool(_PUNY_RE.search(host))


def _percent_encoded(url: str) -> bool:
    """Return True if the URL contains percent-encoded sequences."""
    return bool(_PERCENT_RE.search(url))


def extract_features_from_url(url: str) -> dict:
    """Extract a deterministic feature dictionary from *url*.

    Parameters
    ----------
    url: str
        The URL to analyse.

    Returns
    -------
    dict
        Mapping of feature name to numeric value.
    """

    parsed = urlparse(url)
    # Normalise the scheme to lower case.
    scheme = parsed.scheme.lower()

    host = parsed.hostname or ""
    path = parsed.path or ""
    query = parsed.query or ""
    fragment = parsed.fragment or ""

    # Reconstruct URL for length calculation (without normalization)
    url_length = len(url)

    # Original features (preserved for backward compatibility)
    scheme_flag = 1 if scheme in {"http", "https"} else 0
    has_ip_flag = 1 if _is_ipv4(host) else 0
    has_puny_flag = 1 if _has_punycode(host) else 0
    percent_flag = 1 if _percent_encoded(url) else 0
    hyphen_count = len([c for c in host + path + query + fragment if c == "-"])
    digit_count = len([c for c in url if c.isdigit()])
    # Count subdomains: number of labels minus two (TLD + SLD). Clamp at 0.
    # For IP addresses, we treat as having no subdomains.
    if has_ip_flag:
        subdomains = 0
    else:
        subdomains = max(0, len(host.split(".")) - 2)

    # New features
    hostname_length = len(host)
    path_length = len(path)
    query_length = len(query)
    fragment_length = len(fragment)

    # TLD length (last label in hostname)
    tld_length = 0
    if host and not has_ip_flag:
        host_parts = host.split(".")
        if len(host_parts) >= 1:
            tld_length = len(host_parts[-1])

    hostname_dot_count = host.count(".")
    path_dot_count = path.count(".")
    query_param_count = len([c for c in query if c == "&"]) + (1 if query else 0)
    has_at_sign = 1 if "@" in url else 0
    tilde_count = url.count("~")
    underscore_count = url.count("_")
    colon_count = url.count(":")
    semicolon_count = url.count(";")
    bracket_count = url.count("[") + url.count("]")
    brace_count = url.count("{") + url.count("}")
    parenthesis_count = url.count("(") + url.count(")")
    single_quote_count = url.count("'")
    double_quote_count = url.count('"')
    backtick_count = url.count("`")

    # Return features in canonical order to ensure consistency
    return {
        "url_length": url_length,
        "scheme": scheme_flag,
        "has_ip": has_ip_flag,
        "has_punycode": has_puny_flag,
        "percent_encoding": percent_flag,
        "hyphen_count": hyphen_count,
        "digit_count": digit_count,
        "subdomain_count": subdomains,
        "hostname_length": hostname_length,
        "path_length": path_length,
        "query_length": query_length,
        "fragment_length": fragment_length,
        "tld_length": tld_length,
        "hostname_dot_count": hostname_dot_count,
        "path_dot_count": path_dot_count,
        "query_param_count": query_param_count,
        "has_at_sign": has_at_sign,
        "tilde_count": tilde_count,
        "underscore_count": underscore_count,
        "colon_count": colon_count,
        "semicolon_count": semicolon_count,
        "bracket_count": bracket_count,
        "brace_count": brace_count,
        "parenthesis_count": parenthesis_count,
        "single_quote_count": single_quote_count,
        "double_quote_count": double_quote_count,
        "backtick_count": backtick_count,
    }

__all__ = ["extract_features_from_url"]