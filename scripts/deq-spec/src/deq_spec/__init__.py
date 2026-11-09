"""Validate, format and preview the Deq shape spec (``spec/``). Internal tool, not published."""

from __future__ import annotations


class SpecError(Exception):
    """A spec file is invalid or cannot be expanded."""
