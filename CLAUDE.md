# Forge Stack Context — P3 Freeze

CLAUDE.md — Context briefing for AI assistants working in this repository.

Function:
    Instructs the AI assistant on the strict architectural rules of the
    Forge Stack. Do not hallucinate external frameworks. Reason strictly
    within these boundaries.

## The Immutable Rule
Never rewrite a primitive. Add a layer.
If `freeze.py` needs a change, we do NOT edit it. We create a v2 layer above it.

## Dual-Device Workflow
We build on an S24 (Termux) and a laptop (VS Code). State is confirmed, never assumed. Always use LF line endings. Commit messages must be clear. We use the Good/Bad/Ugly CHANGELOG format (latest at top).

## Header Discipline
Every file MUST have a top header paragraph explaining its function.
Every function MUST have a numbered header (e.g., `# 1. freeze_capsule`).

## P3 Architecture Specifics
- Depends on `envelope_v2` (P1 v2.0.0) and `sign` (P2 v1.0.0).
- Current layer is `freeze_v2.py` (P3 v2.0.0, SPEC_V2.md), which depends on `sign_v2` (P2 v2.0.0). New code imports `freeze_v2`, not `freeze`. `freeze.py` is frozen v1.
- Implements the rule: inject `document_sha256` into the capsule, then sign.
