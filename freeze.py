"""
freeze.py — P3 Freeze primitive layer

Function:
    Implements the freeze rule. Calculates the payload hash, injects
    it into the document_sha256 field, and delegates signing to P2.

Public API:
    1. freeze_capsule          — Hash payload, inject hash, sign.
    2. verify_frozen_capsule   — Verify document hash and signature.

Layer:    P3 — Freeze
Depends:  P1 Envelope v2 (envelope_v2.py), P2 Sign (sign.py)
Consumed: P4 Ledger, P5 Genesis, P6 Canon Verify
Version:  1.0.0 (on freeze; 0.0.0-dev until then)
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import copy
import os
import sys

# Import P1 and P2
sys.path.insert(0, os.path.abspath('../envelope-layer'))
sys.path.insert(0, os.path.abspath('../sign-layer'))
import envelope_v2 as envelope
import sign

# ---------------------------------------------------------------------------
# 1. freeze_capsule
#    Deep copies, zeroes the hash, calculates the payload hash, injects
#    it, and calls P2's sign_capsule.
# ---------------------------------------------------------------------------
def freeze_capsule(capsule, private_key):
    if not isinstance(capsule, dict):
        raise ValueError("Capsule must be a dictionary")
        
    frozen = copy.deepcopy(capsule)
    frozen["document_sha256"] = None
    
    # Calculate hash of payload with None hash
    payload_bytes = envelope.canonical_bytes(frozen)
    payload_hash = envelope.sha256_hex(payload_bytes)
    
    # Inject the hash
    frozen["document_sha256"] = payload_hash
    
    # Delegate signing to P2
    return sign.sign_capsule(frozen, private_key)

# ---------------------------------------------------------------------------
# 2. verify_frozen_capsule
#    Extracts the hash, zeroes it, recalculates the payload hash, and
#    verifies the signature via P2.
# ---------------------------------------------------------------------------
def verify_frozen_capsule(capsule, public_key):
    if not isinstance(capsule, dict) or "document_sha256" not in capsule:
        return False
        
    expected_hash = capsule["document_sha256"]
    if not isinstance(expected_hash, str):
        return False
        
    # Reconstruct the payload by zeroing the hash and removing signature
    payload = copy.deepcopy(capsule)
    payload["document_sha256"] = None
    payload.pop("signature", None)
    
    # Recalculate the hash
    payload_bytes = envelope.canonical_bytes(payload)
    actual_hash = envelope.sha256_hex(payload_bytes)
    
    if actual_hash != expected_hash:
        return False
        
    # Verify the signature via P2
    return sign.verify_capsule(capsule, public_key)
