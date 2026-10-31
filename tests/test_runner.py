import json
import os
from datetime import datetime
import sentencepiece as spm

sp = spm.SentencePieceProcessor()
sp.load('../grok-1/tokenizer.model')

strings = [
    'The answer to life the universe and everything is of course',
    'This repository contains JAX example code for loading and running the Grok-1 open-weights model.',
    'The script loads the checkpoint and samples from the model on a test input.',
    'Due to the large size of the model (314B parameters), a machine with enough GPU memory is required to test the model with the example code.',
    'The implementation of the MoE layer in this repository is not efficient. The implementation was chosen to avoid the need for custom kernels to validate the correctness of the model.',
    'Mixture of 8 Experts (MoE)',
    '2 experts used per token',
    'Supports activation sharding and 8-bit quantization',
    'Maximum Sequence Length (context): 8,192 tokens',
    'SentencePiece tokenizer with 131,072 tokens',
    'Container for the training state.',
    'Performs nucleus filtering on logits.',
    'Return True if regexes in qs match any window of strings in tuple ks.',
    'Using fp32 for the routing prob computation.'
]

results = []
for i, s in enumerate(strings, 1):
    ids = sp.encode(s)
    results.append({
        'id': i,
        'text': s,
        'token_count': len(ids),
        'token_ids': ids
    })

os.makedirs('results', exist_ok=True)
filename = f"results/test_run_tokenizer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

with open(filename, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print(f"Saved tokenizer results to: {filename}")
print(f"Total strings: {len(results)}")
