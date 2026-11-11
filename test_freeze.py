"""
test_freeze.py — P3 Freeze test suite

Function:
    Executable expression of SPEC.md. Written before freeze.py
    per build discipline.

Layer:    P3 — Freeze
Spec:     SPEC.md v1.0.0
Licence:  MSL-1.0
"""

import os
import sys
import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

# Add P1 and P2 to path
sys.path.insert(0, os.path.abspath('../envelope-layer'))
sys.path.insert(0, os.path.abspath('../sign-layer'))

import freeze

@pytest.fixture
def key():
    return Ed25519PrivateKey.generate()

@pytest.fixture
def capsule():
    return {
        "scp_id": "test-123",
        "declaration": "This is a test.",
        "document_sha256": None
    }

def test_freeze_capsule(key, capsule):
    frozen = freeze.freeze_capsule(capsule, key)
    assert frozen["document_sha256"] is not None
    assert len(frozen["document_sha256"]) == 64
    assert "signature" in frozen

def test_freeze_capsule_does_not_mutate(key, capsule):
    original = capsule.copy()
    freeze.freeze_capsule(capsule, key)
    assert capsule == original

def test_verify_frozen_capsule_valid(key, capsule):
    frozen = freeze.freeze_capsule(capsule, key)
    assert freeze.verify_frozen_capsule(frozen, key.public_key()) is True

def test_verify_frozen_capsule_tampered_content(key, capsule):
    frozen = freeze.freeze_capsule(capsule, key)
    frozen["declaration"] = "Tampered!"
    assert freeze.verify_frozen_capsule(frozen, key.public_key()) is False

def test_verify_frozen_capsule_tampered_hash(key, capsule):
    frozen = freeze.freeze_capsule(capsule, key)
    frozen["document_sha256"] = "0" * 64
    assert freeze.verify_frozen_capsule(frozen, key.public_key()) is False

def test_verify_frozen_capsule_missing_hash(key, capsule):
    frozen = freeze.freeze_capsule(capsule, key)
    del frozen["document_sha256"]
    assert freeze.verify_frozen_capsule(frozen, key.public_key()) is False
