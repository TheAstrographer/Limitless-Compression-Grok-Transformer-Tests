import sentencepiece as spm

# Load the official Grok-1 tokenizer
# Adjust the path if your folder structure is slightly different
tokenizer = spm.SentencePieceProcessor()
tokenizer.load("../grok-1/tokenizer.model")   # or the full path if needed

def text_to_token_ids(text: str) -> list[int]:
    """Return the real Grok-1 token ID sequence."""
    return tokenizer.encode(text)

def text_to_token_matrix(text: str, d_model: int = 64) -> list[list[float]]:
    """
    Convert text into a simple numeric matrix that can be fed 
    into the pure TransformerStack (shape: [seq_len, d_model]).
    This is a basic embedding-style mapping for testing.
    """
    token_ids = tokenizer.encode(text)
    # Simple scaling so values stay in a reasonable range
    return [[float(tid) / 1000.0 for _ in range(d_model)] for tid in token_ids]
