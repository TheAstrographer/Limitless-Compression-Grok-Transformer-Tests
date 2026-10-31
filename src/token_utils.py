"""
Tokenization helpers and token observation utilities.
Tokenizer is treated as a separate instance.
"""

from pathlib import Path

def load_repeatable_strings(path: str = "data/repeatable_strings.txt") -> list[str]:
    """Load the fixed repeatable strings from the data file."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Could not find {path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def observe_tokens(tokenizer, text: str) -> list[int]:
    """
    Return the token IDs for a given string.
    Pass in your separate tokenizer instance.
    """

    return tokenizer.encode(text)
