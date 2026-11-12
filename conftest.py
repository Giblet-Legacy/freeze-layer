"""
conftest.py — pytest path setup for P3 Freeze

Function:
    Puts this directory and the sibling P1 and P2 directories
    (../envelope-layer, ../sign-layer) on sys.path, located from this
    file rather than the working directory. pytest loads it before
    collecting tests, so test_freeze.py (frozen v1, cwd-relative
    import) and test_freeze_v2.py both run from any working directory
    (NOTES D1). Contains no functions.

Layer:    P3 — Freeze
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
_P1 = os.path.join(_PARENT, "envelope-layer")
_P2 = os.path.join(_PARENT, "sign-layer")

for _p in (_P1, _P2, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
