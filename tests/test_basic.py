"""
Basic empirical tests for the harness.
"""

from src.token_utils import load_repeatable_strings
from src.hash_utils import hash_token_ids, find_duplicates
from src.transformer_tests import run_basic_test
from src.disclaimer import get_disclaimer, get_referenced_repos

def test_load_strings():
    strings = load_repeatable_strings("data/repeatable_strings.txt")
    assert len(strings) > 0
    assert isinstance(strings[0], str)

def test_hash_and_dedup():
    sample_ids = [1, 2, 3, 1, 2]
    h1 = hash_token_ids(sample_ids)
    h2 = hash_token_ids(sample_ids)
    assert h1 == h2
    duplicates = find_duplicates([h1, h2, "unique"])
    assert len(duplicates) == 1

def test_run_basic():
    result = run_basic_test(tokenizer=None)
    assert "total_strings" in result
    assert "duplicates_found" in result

def test_disclaimer():
    text = get_disclaimer()
    assert "TheAstrographer" in text
    repos = get_referenced_repos()
    assert len(repos) >= 4
