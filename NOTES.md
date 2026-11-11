# NOTES — freeze-layer (P3 Freeze)

NOTES.md — open questions, divergences and decisions for P3 Freeze.

## Open questions
- (none)

## Divergences from v1.2.1 specification
- (none)

## Decisions
- The hash is computed over the canonical bytes of the capsule with 
  `document_sha256` set to None. This isolates the hash to the 
  payload, avoiding infinite recursion.
