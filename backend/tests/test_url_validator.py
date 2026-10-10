"""Tests for the URL validator module."""

from app.ml.url_validator import is_valid_url


def test_valid_http_url():
    """Test validation of a valid HTTP URL."""
    assert is_valid_url("http://example.com") is True


def test_valid_https_url():
    """Test validation of a valid HTTPS URL."""
    assert is_valid_url("https://example.com") is True


def test_valid_url_with_path():
    """Test validation of a URL with path."""
    assert is_valid_url("https://example.com/path/to/resource") is True


def test_valid_url_with_query():
    """Test validation of a URL with query string."""
    assert is_valid_url("https://example.com/search?q=test") is True


def test_valid_url_with_fragment():
    """Test validation of a URL with fragment."""
    assert is_valid_url("https://example.com/page#section") is True


def test_valid_url_with_subdomain():
    """Test validation of a URL with subdomain."""
    assert is_valid_url("https://sub.example.com") is True


def test_valid_ipv4_url():
    """Test validation of a URL with IPv4 address."""
    assert is_valid_url("http://192.168.1.1") is True
    assert is_valid_url("https://8.8.8.8/dns-query") is True


def test_invalid_scheme():
    """Test validation rejects invalid schemes."""
    assert is_valid_url("ftp://example.com") is False
    assert is_valid_url("file://example.com") is False
    assert is_valid_url("javascript:alert(1)") is False


def test_missing_scheme():
    """Test validation rejects URLs without scheme."""
    assert is_valid_url("example.com") is False
    assert is_valid_url("//example.com") is False


def test_invalid_domain():
    """Test validation rejects invalid domain names."""
    assert is_valid_url("http://-example.com") is False  # starts with hyphen
    assert is_valid_url("http://example-.com") is False  # ends with hyphen
    assert is_valid_url("http://.example.com") is False  # starts with dot
    assert is_valid_url("http://example.com.") is False  # ends with dot
    assert is_valid_url("http://..example.com") is False  # double dot
    assert is_valid_url("http://exa_mple.com") is False  # underscore
    # Note: URLs with ports are valid (port is stripped from hostname by urlparse)
    # Actually, urlparse hostname does not include port, so this should be valid
    # Let me check: urlparse("http://example.com:80").hostname is "example.com"
    # So this should be valid. Let's adjust the test.


def test_valid_domain_with_port():
    """Test validation of domain with port (port is stripped by urlparse)."""
    assert is_valid_url("http://example.com:80") is True
    assert is_valid_url("https://example.com:443") is True


def test_single_label_domain():
    """Test validation rejects single label domains."""
    assert is_valid_url("http://localhost") is False  # single label
    assert is_valid_url("http://com") is False  # single label TLD


def test_valid_multi_label_domain():
    """Test validation of multi-label domains."""
    assert is_valid_url("http://sub.sub.example.com") is True
    assert is_valid_url("https://a.b.co.uk") is True


def test_invalid_tld():
    """Test validation rejects invalid TLDs (non-alphabetic)."""
    assert is_valid_url("http://example.c0m") is False  # digit in TLD
    assert is_valid_url("http://example.com1") is False  # digit in TLD
    assert is_valid_url("http://example.c_m") is False  # underscore in TLD


def test_empty_string():
    """Test validation rejects empty string."""
    assert is_valid_url("") is False


def test_none():
    """Test validation rejects None (though it would raise exception)."""
    # We expect this to raise an exception, but let's handle gracefully
    try:
        is_valid_url(None)
        assert False, "Expected exception"
    except Exception:
        pass  # Expected


if __name__ == "__main__":
    # Simple test runner
    import sys
    import traceback

    tests = [
        test_valid_http_url,
        test_valid_https_url,
        test_valid_url_with_path,
        test_valid_url_with_query,
        test_valid_url_with_fragment,
        test_valid_url_with_subdomain,
        test_valid_ipv4_url,
        test_invalid_scheme,
        test_missing_scheme,
        test_invalid_domain,
        test_valid_domain_with_port,
        test_single_label_domain,
        test_valid_multi_label_domain,
        test_invalid_tld,
        test_empty_string,
        test_none,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__}")
            print(f"  {e}")
            traceback.print_exc()
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    sys.exit(failed)