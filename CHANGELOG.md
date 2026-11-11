# CHANGELOG — freeze-layer (P3 Freeze)

CHANGELOG.md — build history for P3 Freeze, latest entry at top.

## [v1.0.0] — 2026-11-11

### Good
- `freeze.py` implemented to SPEC v1.0.0.
- 6/6 pytest tests pass.
- Correctly isolates the hash calculation to the payload.

### Bad
- (none)

### Ugly
- Initial `verify_frozen_capsule` failed because it hashed the signed payload instead of the unsigned payload. Fixed by popping the `signature` key before recalculation.

### Good
- Repository scaffolded: `Giblet-Legacy/freeze-layer` created for P3.
- Depends on P1 Envelope v2.0.0 and P2 Sign v1.0.0.

### Bad
- (none)

### Ugly
- (none)
