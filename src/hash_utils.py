"""
Hashing of tokens and duplicate detection.
"""

import hashlib
from typing import List

def hash_token_ids(token_ids: List[int]) -> str:
    """Create a deterministic hash from a list of token IDs."""
    data = ",".join(map(str, token_ids)).encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def find_duplicates(hashes: List[str]) -> List[str]:
    """Return only the hashes that appear more than once."""
    seen = set()
    duplicates = set()
    for h in hashes:
        if h in seen:
            duplicates.add(h)
        else:
            seen.add(h)

    return sorted(list(duplicates))
