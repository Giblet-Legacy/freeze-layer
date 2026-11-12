# SPEC V2 — freeze-layer (P3 Freeze, strict layer)

SPEC_V2.md — specification for freeze_v2.py, the layer above P3 v1.0.0.

Function:
    Specifies freeze_v2.py, a thin strict layer over the frozen P3
    v1.0.0 primitive (freeze.py). It closes the divergences D1–D4
    recorded in NOTES.md without editing freeze.py (Immutable Rule).

    SPEC.md v1.0.0 remains authoritative for everything this document
    does not change. Where this document is silent, SPEC.md v1.0.0
    applies unchanged.

Layer:     P3 — Freeze, v2 (strict)
Depends:   freeze.py (P3 v1.0.0), sign_v2.py (P2 v2.0.0),
           envelope_v2.py (P1 v2.0.0)
Consumed:  P4 Ledger onward — new code imports freeze_v2, not freeze
Version:   SPEC V2 2.0.0
Licence:   MSL-1.0
Author:    James Gilbert (Giblets Forge)

---

## 1. Compatibility guarantee

- For any capsule with no `"signature"` key, v2 freeze_capsule
  returns the same dict as v1 (Ed25519 is deterministic).
- Every capsule that verifies under v1 verifies under v2.

v2 differs from v1 by **accepting** capsules that v1 froze into an
unverifiable state (§2.2), by **returning False** where v1 crashed or
accepted malformed input (§2.3, §2.4), and by **raising** TypeError
for a wrong public-key type (§2.5). That narrowing is why the major
version is 2.

## 2. Changes from SPEC.md v1.0.0

### 2.1 Location-independent imports (resolves D1)

freeze_v2 locates P1 and P2 relative to its own file:
`<dir of freeze_v2.py>/../envelope-layer` and `../sign-layer`.
Importing freeze_v2 works from any working directory as long as
freeze-layer is on sys.path.

### 2.2 The hash excludes the signature (resolves D2)

SPEC.md §1 hashes the capsule as given; v1 verification removes the
`"signature"` key before re-hashing. A capsule that arrived with a
`"signature"` key (a `null` placeholder, or an already-signed capsule
being re-frozen) was therefore frozen into a state that never
verifies.

v2 makes the rule explicit and symmetric: **the document hash is
computed over the capsule with `"document_sha256": null` and no
`"signature"` key.** freeze_capsule removes any `"signature"` key
from its deep copy before delegating to v1. The signature is then
added by P2, over the capsule including the hash.

### 2.3 Strict signature check (resolves D3)

verify_frozen_capsule checks the signature through sign_v2
(P2 SPEC_V2 §2.2): a malformed signature object (non-str value,
wrong algorithm, extra or missing fields, non-canonical hex) returns
False and never raises.

### 2.4 Strict document hash and no crash on bad content (resolves D4)

verify_frozen_capsule returns False — never raises — unless:

- the capsule is a dict;
- `document_sha256` is a str of exactly 64 characters from `0-9a-f`;
- the capsule can be canonicalised (e.g. no NaN / ±Infinity).

### 2.5 Key type check

verify_frozen_capsule raises TypeError unless `public_key` is an
Ed25519PublicKey, matching P1 and P2 v2. A wrong key type is a caller
bug, not a failed verification.

### 2.6 Unchanged

freeze_capsule still raises ValueError for a non-dict capsule and
TypeError for a wrong private-key type, and never mutates its input.

## 3. Construction rule

freeze_v2 never reimplements a primitive:

- freeze_capsule deep-copies, drops `"signature"`, then calls
  freeze.freeze_capsule.
- verify_frozen_capsule checks key type and hash shape, calls
  sign_v2.verify_capsule, then freeze.verify_frozen_capsule. Both
  must be True.

## 4. Public API

Same two names as P3 v1.0.0, same numbering:

1. freeze_capsule        — v2: drop signature, then v1
2. verify_frozen_capsule — v2: key type, strict shape, sign_v2, then v1

## 5. Test plan (test_freeze_v2.py)

- Public API: two names, both callable.
- freeze_capsule output equals v1 output; v1 ⇄ v2 capsules
  cross-verify.
- D2: a `"signature": null` placeholder and a re-frozen capsule both
  verify.
- freeze_capsule: ValueError for a non-dict; no mutation of a nested
  capsule by freeze or verify.
- verify False results: tampered content, tampered / missing /
  non-str / uppercase / short hash, wrong key, non-dict capsule,
  missing signature.
- D3: int signature value, wrong algorithm, extra field → False.
- D4: NaN in content → False, never raises.
- §2.5: private key, bytes or None as public key → TypeError.
- `import freeze_v2` succeeds from an unrelated working directory.
