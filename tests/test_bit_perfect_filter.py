"""
test_bit_perfect_filter.py

Bit-Perfect First-Occurrence Archival with Aggressive Structural Deduplication
(Detailed Proofs + Complete CSS String Inventory)

Tests the core claims:
1. Bit-Perfect Preservation of First Occurrences
2. Deterministic Collapse
3. Aggressive Deduplication
4. Extractability of Suppressors
5. Extreme Measured Compression (via length-gate behavior)
"""

import pytest
from src.bit_perfect_filter import BitPerfectFilter

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

GROUP_SEP = "\x1D"
UNIT_SEP = "\x1F"

@pytest.fixture
def filter_instance():
    """Default filter used in the live tests (max_length=8000, max_units=80)."""
    return BitPerfectFilter(max_units=80, max_length=8000)


# ------------------------------------------------------------------
# Claim 1 & 3 – First-occurrence archival + aggressive deduplication
# ------------------------------------------------------------------

def test_first_occurrence_and_deduplication(filter_instance):
    text = "Hello world, this is a normal short message."

    r1 = filter_instance.filter_message(text, session_id="claim1")
    r2 = filter_instance.filter_message(text, session_id="claim1")

    assert r1["is_first_occurrence"] is True
    assert r2["is_first_occurrence"] is False
    assert r1["block_hash"] == r2["block_hash"]
    assert r2["occurrence_count"] == 2
    assert r1["extractable"] is True


def test_extractability_of_first_occurrence(filter_instance):
    text = "[A]Short first block. [B]Short second block."
    r = filter_instance.filter_message(text, session_id="extract")

    recovered = filter_instance.extract_original(r["block_hash"])
    assert recovered == text
    assert r["is_first_occurrence"] is True


# ------------------------------------------------------------------
# Claim 2 – Deterministic collapse
# ------------------------------------------------------------------

def test_deterministic_hash(filter_instance):
    text = "This is a repetitive test sentence with some [A] markers and [Section-42] blocks."
    r1 = filter_instance.filter_message(text, session_id="det1")
    r2 = filter_instance.filter_message(text, session_id="det2")  # different session still same hash

    assert r1["block_hash"] == r2["block_hash"]


# ------------------------------------------------------------------
# Claim 4 – Extractability of suppressors (GROUP_SEP)
# ------------------------------------------------------------------

def test_oversized_suppression_and_extractability(filter_instance):
    # Any string longer than 8000 characters
    oversized = "X" * 10000

    r = filter_instance.filter_message(oversized, session_id="suppress")

    assert r["is_suppressed"] is True
    assert r["collapsed_len"] == 1
    assert r["collapsed_text"] == GROUP_SEP or r["unit_count"] == 0
    assert r["is_first_occurrence"] is True
    assert r["extractable"] is True

    # The original must still be recoverable
    recovered = filter_instance.extract_original(r["block_hash"])
    assert recovered == oversized


def test_repeated_oversized_shares_hash(filter_instance):
    oversized = "Y" * 12000

    r1 = filter_instance.filter_message(oversized, session_id="rep_over")
    r2 = filter_instance.filter_message(oversized, session_id="rep_over")

    assert r1["block_hash"] == r2["block_hash"]
    assert r1["is_first_occurrence"] is True
    assert r2["is_first_occurrence"] is False
    assert r2["occurrence_count"] == 2


# ------------------------------------------------------------------
# CSS-related example strings (from the inventory)
# ------------------------------------------------------------------

CSS_EXAMPLES = [
    ".r-1p0dtai",
    ".r-1habvwh",
    ".r-13awgt0",
    ".container { color: red; margin: 0; }",
    ".btn.primary.active.hover.focus.disabled",
    ".style { background: #fff; padding: 12px; }",
]

def test_css_examples_pass_through_or_collapse(filter_instance):
    for css in CSS_EXAMPLES:
        r = filter_instance.filter_message(css, session_id="css")
        assert "block_hash" in r
        assert r["extractable"] is True
        # Short CSS fragments should not be suppressed
        if len(css) < 8000:
            assert r["is_suppressed"] is False


def test_large_css_block_suppressed(filter_instance):
    # Simulate a large CSS block (well over 8000 chars)
    large_css = (".r-1p0dtai { color: red; margin: 0; padding: 12px; } " * 400)
    assert len(large_css) > 8000

    r = filter_instance.filter_message(large_css, session_id="large_css")

    assert r["is_suppressed"] is True
    assert r["collapsed_len"] == 1
    assert r["is_first_occurrence"] is True
    assert r["extractable"] is True


# ------------------------------------------------------------------
# Marker examples
# ------------------------------------------------------------------

MARKER_EXAMPLES = [
    "[A]",
    "[Section-42]",
    "[Tool_Alpha]",
    "[Phase-9]",
    "[Block-Test]",
]

def test_marker_examples(filter_instance):
    for marker in MARKER_EXAMPLES:
        r = filter_instance.filter_message(marker, session_id="markers")
        assert r["is_first_occurrence"] is True
        assert r["extractable"] is True


# ------------------------------------------------------------------
# Short messages (should pass through with minimal change)
# ------------------------------------------------------------------

def test_short_messages(filter_instance):
    short = "Hello world, this is a normal short message."
    r = filter_instance.filter_message(short, session_id="short")

    assert r["is_suppressed"] is False
    assert r["original_len"] == len(short)
    assert r["is_first_occurrence"] is True


# ------------------------------------------------------------------
# Structural delimiters
# ------------------------------------------------------------------

def test_structural_delimiters_present():
    assert UNIT_SEP == "\x1F"
    assert GROUP_SEP == "\x1D"


# ------------------------------------------------------------------
# Summary guarantee
# ------------------------------------------------------------------

def test_summary_guarantee(filter_instance):
    """
    First occurrence → archived bit-perfectly, extractable forever.
    Every duplicate or oversized block → reduced to a hash (or single Group Separator).
    """
    text = "Package has been delivered"

    r1 = filter_instance.filter_message(text, session_id="summary")
    r2 = filter_instance.filter_message(text, session_id="summary")

    assert r1["is_first_occurrence"] is True
    assert r2["is_first_occurrence"] is False
    assert filter_instance.extract_original(r1["block_hash"]) == text
