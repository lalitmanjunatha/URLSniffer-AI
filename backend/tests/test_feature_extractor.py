"""Tests for the feature extractor module."""

from app.ml.feature_extractor import extract_features_from_url

def test_extract_features_basic():
    """Test extraction on a simple URL."""
    url = "https://example.com"
    features = extract_features_from_url(url)
    assert features["url_length"] == len(url)
    assert features["scheme"] == 1  # https is allowed
    assert features["has_ip"] == 0
    assert features["has_punycode"] == 0
    assert features["percent_encoding"] == 0
    assert features["hyphen_count"] == 0
    assert features["digit_count"] == 0
    assert features["subdomain_count"] == 0  # example.com -> 0 subdomains

def test_extract_features_with_subdomain():
    """Test extraction on a URL with subdomains."""
    url = "https://sub.example.com/path"
    features = extract_features_from_url(url)
    assert features["subdomain_count"] == 1  # sub.example.com -> 1 subdomain

def test_extract_features_ip_address():
    """Test extraction on a URL with an IP address."""
    url = "http://192.168.1.1"
    features = extract_features_from_url(url)
    assert features["url_length"] == len(url)
    assert features["scheme"] == 1  # http is allowed
    assert features["has_ip"] == 1
    # No subdomains for IP
    assert features["subdomain_count"] == 0

def test_extract_features_punycode():
    """Test extraction on a URL with punycode."""
    url = "https://xn--example.com"
    features = extract_features_from_url(url)
    assert features["has_punycode"] == 1

def test_extract_features_percent_encoding():
    """Test extraction on a URL with percent encoding."""
    url = "https://example.com%20path"
    features = extract_features_from_url(url)
    assert features["percent_encoding"] == 1

def test_extract_features_hyphens_and_digits():
    """Test extraction on a URL with hyphens and digits."""
    url = "https://ex-ample1.com"
    features = extract_features_from_url(url)
    # Hyphens: one in host
    assert features["hyphen_count"] == 1
    # Digits: one digit '1'
    assert features["digit_count"] == 1

def test_extract_features_empty_string():
    """Test extraction on an empty string."""
    url = ""
    features = extract_features_from_url(url)
    assert features["url_length"] == 0
    assert features["scheme"] == 0
    assert features["has_ip"] == 0
    assert features["has_punycode"] == 0
    assert features["percent_encoding"] == 0
    assert features["hyphen_count"] == 0
    assert features["digit_count"] == 0
    assert features["subdomain_count"] == 0

def test_extract_features_complex():
    """Test a complex URL with multiple features."""
    url = "https://sub.sub2.example-domain123.com:8080/path?query=value#fragment"
    features = extract_features_from_url(url)
    assert features["scheme"] == 1
    # No IP, no punycode, no percent encoding in this example
    assert features["has_ip"] == 0
    assert features["has_punycode"] == 0
    assert features["percent_encoding"] == 0
    # Hyphens: one in host (example-domain123)
    assert features["hyphen_count"] == 1
    # Digits: 2 in sub2, 1,2,3 in example-domain123, 8,0,8,0 in port -> total 8 digits
    assert features["digit_count"] == 8
    # Subdomains: host is sub.sub2.example-domain123.com -> 4 labels -> subdomains = 4-2 = 2.
    assert features["subdomain_count"] == 2
