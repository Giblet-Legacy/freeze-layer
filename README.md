# freeze-layer — P3 Freeze

README.md — repository purpose and layer contract for P3 Freeze.

Function:
    This repository implements primitive layer P3 of the Forge Stack:
    Fills document_sha256 placeholders before signing. It consumes P1
    Envelope v2 and P2 Sign v2 for the underlying cryptographic
    primitives.

Layer:    P3 — Freeze
Depends:  P1 Envelope v2 (envelope_v2.py), expected at ../envelope-layer
          P2 Sign v2 (sign_v2.py), expected at ../sign-layer
Consumed: P4 Ledger, P5 Genesis, P6 Canon Verify
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
Status:   2.0.0 (frozen)

## Files

| File | Role |
| --- | --- |
| `freeze_v2.py` | **Import this.** P3 v2 strict layer (SPEC_V2.md) |
| `freeze.py` | P3 v1.0.0 primitive, frozen, never edited |
| `SPEC.md` / `SPEC_V2.md` | v1 spec / v2 changes over it |
| `test_freeze.py` / `test_freeze_v2.py` | v1 / v2 test suites |
| `conftest.py` | pytest path setup (finds P1 and P2 from its own location, not the working directory) |
| `NOTES.md` | Open questions, divergences (D1–D5), decisions |
| `CHANGELOG.md` | Good / Bad / Ugly, latest at top |

## Run the tests

    python -m pytest -q

This works from this directory or any parent, as long as
`envelope-layer` and `sign-layer` (at v2.0.0) sit beside this
repository.
