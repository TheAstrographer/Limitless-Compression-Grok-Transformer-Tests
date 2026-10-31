# Grok Transformer Test Harness

Empirical test repository for repeatable strings → tokenization → hashing → deduplication logic, run **with / against** the public Grok-1 Transformer.

## Purpose

This harness supports live empiricism tests using Grok’s published repositories while examining concepts from the public repositories under [https://github.com/TheAstrographer](https://github.com/TheAstrographer).

Core logic:
- Feed the same fixed strings
- Obtain the same tokens
- Produce the same hashes
- Detect duplicates cleanly

## Official Grok References

- Model: https://github.com/xai-org/grok-1
- (Optional) Build / CLI: https://github.com/xai-org/grok-build

Users should clone the official Grok-1 repository separately. This harness does **not** vendor the full model source or weights.

## TheAstrographer Repositories Under Test

- https://github.com/TheAstrographer/Lossless-Extraction
- https://github.com/TheAstrographer/The-First-Ever-Softmax-Temperature-Spherical-Attention-Map
- https://github.com/TheAstrographer/The-Tanarcantau-Shannon-Entropy-JCRIN-Definitive-Infinity
- https://github.com/TheAstrographer/JCRIN-Radial-Emergence

See `src/disclaimer.py` for the full testing boundary and integrity notice.


Transformer Test Steps (Empirical Harness)

Here is the clean, ordered list of steps for running the Grok-1 Transformer empirical tests:

Prepare the environment
   Clone this test harness repository.
   Clone the official Grok-1 repository separately:  
     https://github.com/xai-org/grok-1
   Place the fixed repeatable strings in data/repeatable_strings.txt.

Load the fixed strings
   Use src/token_utils.py → load_repeatable_strings().
   These strings must remain unchanged so results stay deterministic.

Tokenize the strings
   Pass each string through the official Grok-1 SentencePiece tokenizer (or your separate tokenizer instance).
   Record the exact token ID sequences.

Generate deterministic hashes
   Hash the token ID sequences using src/hash_utils.py → hash_token_ids().
   Optionally hash selected intermediate activations if a forward pass is performed.

Detect duplicates
   Run find_duplicates() on the list of hashes.
   Any repeated hash indicates a duplicate token sequence.

Optional: Run full empirical test
   Call src/transformer_tests.py → run_basic_test().
   This executes the complete flow:  
     strings → tokens → hashes → duplicate detection.

Optional advanced helpers
   Use arcan_jcrin_helpers.py for temperature / entropy / radial checks.
   Use lossless_extraction_helpers.py for length-gate and first-occurrence logic.
   Reference disclaimer.py for the testing boundary.

Live validation with Grok
   Use controlled hard prompt injection against Grok to verify that the same strings produce consistent tokenization and hashing behavior under the public Grok-1 Transformer logic.
   Record results for empiricism.

Document outcomes
   Note total strings processed, unique hashes, and any duplicates found.
   Keep all results tied to the fixed string list for reproducibility.

This sequence follows the exact core logic you defined:  
feed the same strings → get the same tokens → get the same hashes → easily detect duplicates.
