"""
test_freeze_v2.py — P3 Freeze v2 (strict layer) test suite

Function:
    Executable expression of SPEC_V2.md §5. Written before
    freeze_v2.py and run red first. Proves two things: (1) v2 stays
    compatible with the frozen v1 primitive, so v1 frozen capsules
    still verify; (2) v2 freezes, rejects or raises where SPEC
    requires and v1 did not (NOTES.md D1–D4).

Functions in this file:
    Fixtures:
    1.  key                                — fresh Ed25519 private key
    2.  capsule                            — nested test capsule
    Tests (pytest-collected):
    3.  test_public_api                    — two names, both callable
    4.  test_freeze_identity_with_v1       — same dict as v1
    5.  test_capsules_cross_verify         — v1 ⇄ v2
    6.  test_freeze_with_signature_key     — D2: placeholder, re-freeze
    7.  test_freeze_non_dict               — ValueError
    8.  test_no_mutation_nested            — freeze and verify are pure
    9.  test_verify_false_results          — tamper, wrong key, bad shape
    10. test_verify_malformed_signature    — D3: False, never raises
    11. test_verify_non_canonical_content  — D4: False, never raises
    12. test_verify_key_type_errors        — §2.5 TypeError
    13. test_import_from_any_cwd           — D1

Layer:    P3 — Freeze, v2 (strict)
Spec:     SPEC_V2.md 2.0.0 (over SPEC.md v1.0.0)
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import copy
import os
import subprocess
import sys

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import freeze
import freeze_v2

HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# 1. key
# ---------------------------------------------------------------------------
@pytest.fixture
def key():
    return Ed25519PrivateKey.generate()


# ---------------------------------------------------------------------------
# 2. capsule
# ---------------------------------------------------------------------------
@pytest.fixture
def capsule():
    return {
        "scp_id": "test-123",
        "declaration": "This is a test.",
        "claims": {"tags": ["a", "b"], "n": 3},
        "document_sha256": None,
    }


# ---------------------------------------------------------------------------
# 3. test_public_api
# ---------------------------------------------------------------------------
def test_public_api():
    for name in ("freeze_capsule", "verify_frozen_capsule"):
        assert callable(getattr(freeze_v2, name))


# ---------------------------------------------------------------------------
# 4. test_freeze_identity_with_v1
# ---------------------------------------------------------------------------
def test_freeze_identity_with_v1(key, capsule):
    assert freeze_v2.freeze_capsule(capsule, key) == freeze.freeze_capsule(capsule, key)


# ---------------------------------------------------------------------------
# 5. test_capsules_cross_verify
# ---------------------------------------------------------------------------
def test_capsules_cross_verify(key, capsule):
    pub = key.public_key()
    assert freeze_v2.verify_frozen_capsule(freeze.freeze_capsule(capsule, key), pub) is True
    assert freeze.verify_frozen_capsule(freeze_v2.freeze_capsule(capsule, key), pub) is True


# ---------------------------------------------------------------------------
# 6. test_freeze_with_signature_key
#    D2: v1 froze these into a state that never verified.
# ---------------------------------------------------------------------------
def test_freeze_with_signature_key(key, capsule):
    pub = key.public_key()

    placeholder = dict(capsule, signature=None)
    assert freeze.verify_frozen_capsule(freeze.freeze_capsule(placeholder, key), pub) is False
    assert freeze_v2.verify_frozen_capsule(freeze_v2.freeze_capsule(placeholder, key), pub) is True

    frozen = freeze_v2.freeze_capsule(capsule, key)
    refrozen = freeze_v2.freeze_capsule(frozen, key)
    assert freeze_v2.verify_frozen_capsule(refrozen, pub) is True
    assert refrozen == frozen

    other = Ed25519PrivateKey.generate()
    resigned = freeze_v2.freeze_capsule(frozen, other)
    assert freeze_v2.verify_frozen_capsule(resigned, other.public_key()) is True
    assert freeze_v2.verify_frozen_capsule(resigned, pub) is False


# ---------------------------------------------------------------------------
# 7. test_freeze_non_dict
# ---------------------------------------------------------------------------
def test_freeze_non_dict(key):
    for bad in (None, [], "capsule", 1):
        with pytest.raises(ValueError):
            freeze_v2.freeze_capsule(bad, key)


# ---------------------------------------------------------------------------
# 8. test_no_mutation_nested
# ---------------------------------------------------------------------------
def test_no_mutation_nested(key, capsule):
    original = copy.deepcopy(capsule)
    frozen = freeze_v2.freeze_capsule(capsule, key)
    assert capsule == original

    frozen_copy = copy.deepcopy(frozen)
    freeze_v2.verify_frozen_capsule(frozen, key.public_key())
    assert frozen == frozen_copy


# ---------------------------------------------------------------------------
# 9. test_verify_false_results
# ---------------------------------------------------------------------------
def test_verify_false_results(key, capsule):
    pub = key.public_key()
    frozen = freeze_v2.freeze_capsule(capsule, key)
    h = frozen["document_sha256"]

    cases = [
        dict(frozen, declaration="Tampered!"),
        dict(frozen, claims={"tags": ["a"], "n": 3}),
        dict(frozen, document_sha256="0" * 64),
        dict(frozen, document_sha256=None),
        dict(frozen, document_sha256=123),
        dict(frozen, document_sha256=h.upper()),
        dict(frozen, document_sha256=h[:-1]),
        {k: v for k, v in frozen.items() if k != "document_sha256"},
        {k: v for k, v in frozen.items() if k != "signature"},
        dict(frozen, signature=None),
    ]
    for bad in cases:
        assert freeze_v2.verify_frozen_capsule(bad, pub) is False

    assert freeze_v2.verify_frozen_capsule(frozen, Ed25519PrivateKey.generate().public_key()) is False
    for bad in (None, [], "capsule", 1):
        assert freeze_v2.verify_frozen_capsule(bad, pub) is False


# ---------------------------------------------------------------------------
# 10. test_verify_malformed_signature
#     D3: v1 raised on an int value and accepted algorithm "RSA".
# ---------------------------------------------------------------------------
def test_verify_malformed_signature(key, capsule):
    pub = key.public_key()
    frozen = freeze_v2.freeze_capsule(capsule, key)
    sig = frozen["signature"]

    for bad_sig in (
        dict(sig, value=123),
        dict(sig, value=sig["value"].upper()),
        dict(sig, algorithm="RSA"),
        dict(sig, extra="x"),
        {k: v for k, v in sig.items() if k != "algorithm"},
    ):
        assert freeze_v2.verify_frozen_capsule(dict(frozen, signature=bad_sig), pub) is False


# ---------------------------------------------------------------------------
# 11. test_verify_non_canonical_content
#     D4: v1 raised ValueError from canonicalisation.
# ---------------------------------------------------------------------------
def test_verify_non_canonical_content(key, capsule):
    pub = key.public_key()
    frozen = freeze_v2.freeze_capsule(capsule, key)
    for value in (float("nan"), float("inf"), float("-inf")):
        assert freeze_v2.verify_frozen_capsule(dict(frozen, x=value), pub) is False


# ---------------------------------------------------------------------------
# 12. test_verify_key_type_errors
# ---------------------------------------------------------------------------
def test_verify_key_type_errors(key, capsule):
    frozen = freeze_v2.freeze_capsule(capsule, key)
    for bad_key in (key, key.public_key().public_bytes_raw(), None):
        with pytest.raises(TypeError):
            freeze_v2.verify_frozen_capsule(frozen, bad_key)


# ---------------------------------------------------------------------------
# 13. test_import_from_any_cwd
#     D1: run from the parent directory with only freeze-layer on the path.
# ---------------------------------------------------------------------------
def test_import_from_any_cwd():
    code = f"import sys; sys.path.insert(0, {HERE!r}); import freeze_v2"
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=os.path.dirname(HERE),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
