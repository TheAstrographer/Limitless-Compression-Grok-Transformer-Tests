"""
Main empirical test logic for the Grok Transformer harness.
Logic: feed the same strings → get the same tokens → get the same hashes → detect duplicates
"""

from .token_utils import load_repeatable_strings, observe_tokens
from .hash_utils import hash_token_ids, find_duplicates

def run_basic_test(tokenizer=None) -> dict:
    """
    Core test using the repeatable strings.
    """
    strings = load_repeatable_strings("data/repeatable_strings.txt")
    
    all_hashes = []
    
    for text in strings:
        if tokenizer is not None:
            token_ids = observe_tokens(tokenizer, text)
            h = hash_token_ids(token_ids)
            all_hashes.append(h)
        else:
            # Placeholder when tokenizer is not yet connected
            all_hashes.append(hash_token_ids([ord(c) for c in text[:20]]))  # simple fallback
    
    duplicates = find_duplicates(all_hashes)
    
    return {
        "total_strings": len(strings),
        "unique_hashes": len(set(all_hashes)),
        "duplicates_found": len(duplicates),
        "duplicate_hashes": duplicates

    }
