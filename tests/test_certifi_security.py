"""Offline checks for GHSA-6q48-6c7w-9gw2; no TLS verification bypasses."""
from importlib.metadata import version
import hashlib
import re
from pathlib import Path
import ssl

import certifi
import httpx
import requests

ROOT = Path(__file__).resolve().parents[1]


def test_certifi_pin_and_installed_version():
    assert "certifi==2026.10.19" in (ROOT / "requirements.txt").read_text().splitlines()
    assert version("certifi") == "2026.10.19"


def test_compromised_emsign_root_is_absent_from_certifi_bundle():
    context = ssl.create_default_context(cafile=certifi.where())
    roots = context.get_ca_certs()
    assert roots, "The trust bundle must remain usable, not be empty."
    # Parse the supplied PEM itself: host SSL hooks can append system trust roots
    # even when an explicit cafile is given. Do not confuse those with certifi.
    pem_certificates = re.findall(
        r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----",
        Path(certifi.where()).read_text(), re.DOTALL,
    )
    fingerprints = {
        hashlib.sha256(ssl.PEM_cert_to_DER_cert(pem)).hexdigest()
        for pem in pem_certificates
    }
    assert fingerprints
    # emSign ECC Root CA - G3, fingerprint from the previous official bundle.
    assert "86a1ecba089c4a8d3bbe2734c612ba341d813e043cf9e8a862cd5c57a36bbe6b" not in fingerprints
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True


def test_requests_defaults_to_patched_bundle():
    assert Path(requests.certs.where()).resolve() == Path(certifi.where()).resolve()
    assert Path(requests.utils.DEFAULT_CA_BUNDLE_PATH).resolve() == Path(certifi.where()).resolve()
    with requests.Session() as session:
        assert session.verify is True


def test_httpx_loads_patched_bundle_with_verification_enabled():
    # Use an explicit context to verify normal TLS settings without networking.
    context = ssl.create_default_context(cafile=certifi.where())
    with httpx.Client(verify=context, trust_env=False) as client:
        assert client is not None
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True
