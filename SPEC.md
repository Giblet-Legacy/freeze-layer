# SPEC — freeze-layer (P3 Freeze)

SPEC.md — the complete layer specification for P3 Freeze.

Function:
    This document is the authoritative specification for primitive
    layer P3 of the Forge Stack. It defines the freeze rule: how to
    calculate and inject a document hash into a capsule before signing.

Layer:     P3 — Freeze
Depends:   P1 Envelope v2, P2 Sign
Consumed:  P4 Ledger, P5 Genesis, P6 Canon Verify
Version:   SPEC 1.0.0
Licence:   MSL-1.0
Author:    James Gilbert (Giblets Forge)

## 1. The Freeze Rule

The v1.2.1 architecture states: "Fills document_sha256 before signing."

A capsule often needs to reference the hash of its own payload (e.g., a claim about a specific document). This creates a self-reference problem: injecting the hash changes the document, which changes the hash.

P3 solves this deterministically.

`freeze_capsule(capsule: dict, private_key: Ed25519PrivateKey) -> dict`

The exact algorithm:
1. Deep copy the input `capsule` dict.
2. Set `"document_sha256": None` in the copy.
3. Pass the copy to `envelope_v2.canonical_bytes()`.
4. Hash the resulting bytes via `envelope_v2.sha256_hex()`.
5. Set `"document_sha256"` in the copy to the resulting hex string.
6. Pass the updated copy to `sign.sign_capsule()`.
7. Return the signed, frozen capsule.

## 2. Verification Rule

`verify_frozen_capsule(capsule: dict, public_key: Ed25519PublicKey) -> bool`

The exact algorithm:
1. Check that `"document_sha256"` exists and is a string.
2. Deep copy the capsule.
3. Extract the hash, then set `"document_sha256": None` in the copy.
4. Canonicalise the copy and compute the hash.
5. If the computed hash does not match the extracted hash, return False.
6. If they match, verify the signature via `sign.verify_capsule()`.

## 3. Function Contracts

### 3.1 freeze_capsule(capsule: dict, private_key) -> dict
- Input: A dictionary, an unlocked Ed25519 private key.
- Output: A signed dictionary with a populated document_sha256.
- Failure modes: ValueError if capsule is not a dict.
- Purity: Pure function.

### 3.2 verify_frozen_capsule(capsule: dict, public_key) -> bool
- Input: A frozen capsule dictionary.
- Output: True if both the document hash and the signature are valid, False otherwise.
- Purity: Pure function.
