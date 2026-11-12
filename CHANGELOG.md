# CHANGELOG — freeze-layer (P3 Freeze)

CHANGELOG.md — build history for P3 Freeze, latest entry at top.

Function:
    Records the Good / Bad / Ugly of every build step for this layer.
    Updated at every sign-off. The format never changes shape, even
    when a section is empty.

## [v2.0.0] — 2026-11-12

### Good

- `freeze_v2.py`: strict layer above the frozen P3 v1.0.0, specified
  in `SPEC_V2.md` before any code. It hashes and signs through
  freeze.py and sign_v2, so v1 frozen capsules still verify (tested
  both ways).
- Resolves NOTES D1–D4: P1/P2 are imported from the file's own
  location; the hash excludes `"signature"`, so placeholder and
  re-frozen capsules verify; signatures are checked strictly via
  sign_v2; malformed or non-canonical capsules return False instead
  of crashing.
- `test_freeze_v2.py`: 11 tests, written before freeze_v2.py and run
  red first (10 failed). The full suite passes 17/17 from inside the
  repo and from its parent directory.
- `conftest.py`: pytest finds P1 and P2 from its own location, so the
  frozen test_freeze.py also runs from any working directory.

### Bad

- Review found freeze.py v1.0.0 froze any capsule carrying a
  `"signature"` key into a state that never verifies (NOTES D2). The
  v1.0.0 tests only used capsules without that key.
- verify_frozen_capsule inherited P2 v1's crashes and its acceptance
  of any algorithm (NOTES D3).

### Ugly

- freeze.py's header and test_freeze.py's missing function headers
  are stale but frozen (NOTES D5). They stay as they are.
- v2 verify_frozen_capsule checks the signature twice (sign_v2, then
  v1 via sign.py). This is the cost of never reimplementing the v1
  hash check.

## [v1.0.0] — 2026-11-11

### Good

- `freeze.py` implemented to SPEC v1.0.0.
- 6/6 pytest tests pass.
- Correctly isolates the hash calculation to the payload.

### Bad

- (none recorded at the time; see v2.0.0 Bad)

### Ugly

- Initial `verify_frozen_capsule` failed because it hashed the signed
  payload instead of the unsigned payload. Fixed by popping the
  `signature` key before recalculation. freeze_capsule was not given
  the same rule (see v2.0.0, NOTES D2).

## [v0.0.0-dev] — 2026-11-11

### Good

- Repository scaffolded: `Giblet-Legacy/freeze-layer` created for P3.
- Depends on P1 Envelope v2.0.0 and P2 Sign v1.0.0.

### Bad

- (none)

### Ugly

- (none)
