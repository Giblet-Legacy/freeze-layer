# NOTES — freeze-layer (P3 Freeze)

NOTES.md — open questions, divergences and decisions for P3 Freeze.

Function:
    Records open questions and divergences between freeze.py v1.0.0
    and SPEC.md v1.0.0. freeze.py is never edited (Immutable Rule), so
    a fix means a new layer above it, after a SPEC version describes
    it. Each divergence below names the layer and section that
    resolves it.

## Open questions

- (none)

## Divergences — freeze.py v1.0.0 vs SPEC.md v1.0.0

Found in review 2026-11-12. Each was reproduced by a probe before the
fix. D1–D4 are resolved by `freeze_v2.py` (SPEC_V2.md 2.0.0);
freeze.py is unchanged.

- **D1 — CWD-relative P1/P2 imports.** `freeze.py:24-25` and
  `test_freeze.py:19-20` insert `os.path.abspath('../envelope-layer')`
  and `'../sign-layer'`, which resolve against the working directory.
  Running pytest from the parent directory failed with
  `ModuleNotFoundError: envelope_v2`. **Resolved:** SPEC_V2 §2.1;
  freeze_v2 locates P1/P2 from `__file__`. `conftest.py` does the
  same for pytest, so the frozen test_freeze.py also runs from
  anywhere.
- **D2 — Frozen capsules that never verify.** freeze_capsule hashes
  the capsule as given, but verify_frozen_capsule removes
  `"signature"` before re-hashing (a divergence from SPEC §2, which
  does not mention it). Any input with a `"signature"` key — a `null`
  placeholder, or re-freezing a signed capsule — was frozen and
  signed but always verified False. **Resolved:** SPEC_V2 §2.2; the
  hash excludes `"signature"` on both sides.
- **D3 — Inherited P2 v1 signature defects.** verify_frozen_capsule
  calls `sign.verify_capsule` (v1), so a `"value"` of `123` raised
  `TypeError` and `"algorithm": "RSA"` verified True (P2 NOTES D2,
  D3). **Resolved:** SPEC_V2 §2.3; signature checked via sign_v2.
- **D4 — verify raises on content with no canonical form.** A
  capsule containing NaN raised `ValueError` from envelope_v2. SPEC
  §3.2 says False. **Resolved:** SPEC_V2 §2.4.
- **D5 — Documentation drift in frozen files (not fixed).**
  `freeze.py`'s header still reads `Version: 1.0.0 (on freeze;
  0.0.0-dev until then)`, and the functions in test_freeze.py have no
  numbered headers (CLAUDE.md Header Discipline). Both files are
  frozen and left as they are; freeze_v2.py and test_freeze_v2.py
  follow the discipline.

## Divergences from v1.2.1 specification

- (none)

## Decisions

- The hash is computed over the canonical bytes of the capsule with
  `document_sha256` set to None. This isolates the hash to the
  payload, avoiding infinite recursion.
- 2026-11-12 — from v2 the hash also excludes the `"signature"` key
  (SPEC_V2 §2.2). Order is fixed: hash first, then sign over the
  capsule including the hash. Any old signature is discarded on
  freeze, so re-freezing with a new key re-signs it.
- 2026-11-12 — freeze_v2 imports `sign_v2` (P2 v2.0.0), not `sign`,
  as P2's CLAUDE.md directs for new code. freeze.py v1 still imports
  `sign` and is unchanged.
- 2026-11-12 — a wrong public-key type raises TypeError in v2
  verify_frozen_capsule, matching P1 and P2 v2. v1 returned False for
  raw bytes and raised for a private key.
