"""Tests for version tracking."""
import re

from debate.shared.version import VERSION, get_version


def test_version_format():
    r"""Test that version matches \d+\.\d+ format."""
    assert re.match(r"^\d+\.\d+$", VERSION)
    assert re.match(r"^\d+\.\d+$", get_version())
