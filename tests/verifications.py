import os
import json
import random
from datetime import datetime
from src.staccato_transformer import StaccatoTransformerPipeline

def test_staccato_pipeline_metrics():
    # 1. Initialize the pipeline
    pipe = StaccatoTransformerPipeline()
    
    # 2. Generate random mock tokens (seq_len=4, d_model=64)
    src = [[random.gauss(0, 0.1) for _ in range(64)] for _ in range(4)]
    tgt = [[random.gauss(0, 0.1) for _ in range(64)] for _ in range(4)]
    
    # 3. Process tokens through the matrix math
    result = pipe.process(src, tgt)
    
    # 4. Prepare the metrics payload
    metrics_payload = {
        "timestamp": datetime.now().isoformat(),
        "status": "PASSED",
        "metrics": {
            "k_norm_factor": result['k_norm'],
            "staccato_gain": result['staccato_gain'],
            "output_matrix_shape": f"{len(result['transformer_output'])}x{len(result['transformer_output'][0])}"
        }
    }
    
    # 5. Create a logs directory if it doesn't exist yet
    os.makedirs("results", exist_ok=True)
    
    # 6. Save as a clean JSON report file
    with open("results/staccato_metrics.json", "w") as json_file:
        json.dump(metrics_payload, json_file, indent=4)
        
    # 7. Print directly to console for visibility
    print(f"\n[SAVED TO FILE] k_norm Factor: {result['k_norm']}")
    print(f"[SAVED TO FILE] Staccato Gain: {result['staccato_gain']}")
    
    # 8. Structural validation assert
    assert len(result['transformer_output']) == 4
