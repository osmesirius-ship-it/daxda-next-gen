"""Frozen V9 firewall package.

The V9 source files are copied byte-for-byte from the stabilized candidate.
This package shim only makes the original absolute ``cl20`` import resolvable.
"""
from __future__ import annotations

import sys
from . import cl20 as _cl20

sys.modules.setdefault("cl20", _cl20)

