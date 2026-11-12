"""
freeze_v2.py — P3 Freeze v2, strict layer over the frozen v1 primitive

Function:
    The layer new code imports instead of freeze.py. It finds P1 and
    P2 from its own location rather than the working directory,
    excludes any "signature" key from the document hash so that every
    frozen capsule verifies, checks signatures through sign_v2, and
    returns False instead of crashing on malformed input
    (SPEC_V2.md §2). It never reimplements a primitive: every hash and
    signature goes through freeze.py and P2, so every v1 frozen
    capsule verifies through v2 (SPEC_V2.md §1, §3).

    freeze.py is not edited (Immutable Rule). This file is the
    "add a layer" half of that rule.

Public API (same names and numbering as P3 v1.0.0):
    1. freeze_capsule        — drop signature, then v1
    2. verify_frozen_capsule — key type check, strict hash shape,
                               sign_v2, then v1

Internal helpers (not exported):
    3. _require_public_key — TypeError unless Ed25519PublicKey
    4. _is_lower_hex       — str of exact length, chars 0-9a-f only

Layer:    P3 — Freeze, v2 (strict)
Depends:  freeze.py (P3 v1.0.0), sign_v2.py (P2 v2.0.0),
          envelope_v2.py (P1 v2.0.0)
Consumed: P4 Ledger, P5 Genesis, P6 Canon Verify
Spec:     SPEC_V2.md 2.0.0 (over SPEC.md v1.0.0)
Version:  2.0.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import copy
import os
import sys

# Locate P1 and P2 from this file, not the working directory
# (SPEC_V2 §2.1). Must run before importing freeze.py, whose own path
# inserts are cwd-relative and only correct from inside freeze-layer.
_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
for _p in (os.path.join(_PARENT, "envelope-layer"), os.path.join(_PARENT, "sign-layer")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

import freeze as _v1
import sign_v2 as _sign

_HEX_LOWER = frozenset("0123456789abcdef")


# ---------------------------------------------------------------------------
# 3. _require_public_key
#    TypeError unless public_key is an Ed25519PublicKey (SPEC_V2 §2.5).
# ---------------------------------------------------------------------------
def _require_public_key(public_key):
    if not isinstance(public_key, Ed25519PublicKey):
        raise TypeError(f"public_key must be Ed25519PublicKey, got {type(public_key).__name__}")


# ---------------------------------------------------------------------------
# 4. _is_lower_hex
#    True only for a str of exactly `length` lowercase hex characters.
# ---------------------------------------------------------------------------
def _is_lower_hex(value, length):
    return isinstance(value, str) and len(value) == length and set(value) <= _HEX_LOWER


# ---------------------------------------------------------------------------
# 1. freeze_capsule
#    Deep copy, drop any "signature" key so the hash covers the same
#    bytes verification re-hashes (SPEC_V2 §2.2), then v1.
# ---------------------------------------------------------------------------
def freeze_capsule(capsule, private_key):
    if not isinstance(capsule, dict):
        raise ValueError("Capsule must be a dictionary")

    unsigned = copy.deepcopy(capsule)
    unsigned.pop("signature", None)

    return _v1.freeze_capsule(unsigned, private_key)


# ---------------------------------------------------------------------------
# 2. verify_frozen_capsule
#    Key type check (raises), then strict hash shape, strict signature
#    via sign_v2, then v1's hash check. Malformed input or content
#    that cannot be canonicalised is False, never an exception
#    (SPEC_V2 §2.3, §2.4).
# ---------------------------------------------------------------------------
def verify_frozen_capsule(capsule, public_key):
    _require_public_key(public_key)
    if not isinstance(capsule, dict):
        return False
    if not _is_lower_hex(capsule.get("document_sha256"), 64):
        return False

    try:
        if not _sign.verify_capsule(capsule, public_key):
            return False
        return _v1.verify_frozen_capsule(capsule, public_key)
    except (ValueError, TypeError):
        # Content that has no canonical form (e.g. NaN, ±Infinity).
        return False
