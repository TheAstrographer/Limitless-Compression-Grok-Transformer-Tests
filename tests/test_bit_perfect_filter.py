"""
test_bit_perfect_filter.py
Bit-Perfect First-Occurrence Archival tests
"""

import pytest
from src.bit_perfect_filter import BitPerfectFilter

GROUP_SEP = "\x1D"
UNIT_SEP = "\x1F"

@pytest.fixture
def f():
    return BitPerfectFilter(max_units=80, max_length=8000)

def test_first_occurrence(f):
    text = "Hello world, this is a normal short message."
    r1 = f.filter_message(text, session_id="s1")
    r2 = f.filter_message(text, session_id="s1")

    assert r1["is_first_occurrence"] is True
    assert r2["is_first_occurrence"] is False
    assert r1["block_hash"] == r2["block_hash"]
    assert r2["occurrence_count"] == 2

def test_extractability(f):
    text = "[A]Short first block. [B]Short second block."
    r = f.filter_message(text, session_id="s2")
    recovered = f.extract_original(r["block_hash"])
    assert recovered == text

def test_oversized_suppression(f):
    oversized = "X" * 10000
    r = f.filter_message(oversized, session_id="s3")

    assert r["is_suppressed"] is True
    assert r["collapsed_len"] == 1
    assert r["is_first_occurrence"] is True
    assert f.extract_original(r["block_hash"]) == oversized

def test_css_short(f):
    css = ".container { color: red; margin: 0; }"
    r = f.filter_message(css, session_id="s4")
    assert r["is_suppressed"] is False
    assert r["extractable"] is True

def test_large_css_suppressed(f):
    large_css = (".r-1p0dtai { color: red; } " * 500)
    r = f.filter_message(large_css, session_id="s5")
    assert r["is_suppressed"] is True
    assert r["collapsed_len"] == 1

def test_empty_string(f):
    r = f.filter_message("", session_id="char")
    assert r["collapsed_len"] == 0
    assert r["is_suppressed"] is False


def test_single_character(f):
    r = f.filter_message("A", session_id="char")
    assert r["is_first_occurrence"] is True
    assert r["is_suppressed"] is False
    assert f.extract_original(r["block_hash"]) == "A"


def test_whitespace_only(f):
    r = f.filter_message("   \n\t  ", session_id="char")
    # Should collapse aggressively
    assert r["collapsed_len"] <= 1


def test_exactly_8000_chars(f):
    text = "X" * 8000
    r = f.filter_message(text, session_id="char")
    assert r["is_suppressed"] is False   # exactly at the limit should pass


def test_8001_chars_suppressed(f):
    text = "X" * 8001
    r = f.filter_message(text, session_id="char")
    assert r["is_suppressed"] is True
    assert r["collapsed_len"] == 1
    assert r["collapsed_text"] == "\x1D"


def test_control_characters(f):
    text = "Hello\x1FWorld\x1DTest"
    r = f.filter_message(text, session_id="char")
    assert r["extractable"] is True


def test_marker_characters(f):
    text = "[A][Section-42][Tool_Alpha]"
    r = f.filter_message(text, session_id="char")
    assert r["is_first_occurrence"] is True
    assert f.extract_original(r["block_hash"]) == text
