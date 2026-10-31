import random
from src.staccato_transformer import StaccatoTransformerPipeline

def test_staccato_pipeline_metrics():
    # 1. Initialize the pipeline
    pipe = StaccatoTransformerPipeline()
    
    # 2. Generate random mock tokens (seq_len=4, d_model=64)
    src = [[random.gauss(0, 0.1) for _ in range(64)] for _ in range(4)]
    tgt = [[random.gauss(0, 0.1) for _ in range(64)] for _ in range(4)]
    
    # 3. Process tokens through the matrix math
    result = pipe.process(src, tgt)
    
    # 4. Print your specific pipeline constants directly to the console
    print(f"\n[STACCATO METRICS] k_norm Factor: {result['k_norm']}")
    print(f"[STACCATO METRICS] Staccato Gain: {result['staccato_gain']}")
    
    # 5. Safety check to make sure matrix output dimensions are correct
    assert len(result['transformer_output']) == 4
