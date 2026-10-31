import math
import random
from decimal import Decimal, getcontext
from typing import Dict, List, Union

getcontext().prec = 28

# ============================================================
# 0. KERNEL DIVISION BRIDGE + STACCATO SPECIAL
# ============================================================
class KernelDivisionBridge:
    """Exact constants from the repository."""
    def __init__(self):
        self.psi = Decimal("0.1503378808")
        self.Re_tau = Decimal("1.4129651365")
        self.cos_psi = Decimal("0.9887205")
        self.sin_Re_tau = Decimal("0.98768834059")

        numerator = self.cos_psi * self.Re_tau
        self.K = numerator / self.sin_Re_tau
        self.k_norm = Decimal(1) / self.K          # ≈ 0.7071

    @property
    def k_norm_float(self) -> float:
        return float(self.k_norm)


class LowCadenceVMM:
    """
    Low-cadence (staccato) specialization of the VMM equation:

        I_staccato = (k_norm / 0.47) * Σ (V_i * G_i)
                   ≈ 1.5045 * Σ (V_i * G_i)
    """
    def __init__(self):
        self.bridge = KernelDivisionBridge()
        self.N_low = Decimal("0.47")
        self.gain = self.bridge.k_norm / self.N_low  # ≈ 1.5045

    def to_signed_int32(self, val: int) -> int:
        if val & 0x80000000:
            return val - 0x100000000
        return val

    def raw_dot_product(self, V: List[int], G: List[int]) -> int:
        if len(V) != len(G):
            raise ValueError("V and G must have the same length")
        acc = 0
        for v, g in zip(V, G):
            acc += self.to_signed_int32(v) * self.to_signed_int32(g)
        return acc

    def compute(self, V: List[int], G: List[int]) -> Dict[str, Union[int, float, str]]:
        raw = self.raw_dot_product(V, G)
        raw_dec = Decimal(raw)

        kernel_scaled = raw_dec * self.bridge.k_norm
        I_low = kernel_scaled / self.N_low

        return {
            "raw_dot_product": raw,
            "k_norm": float(self.bridge.k_norm),
            "N_low": float(self.N_low),
            "gain": float(self.gain),
            "kernel_scaled": int(kernel_scaled.to_integral_value()),
            "I_normalized_low": float(I_low),
            "I_normalized_low_sci": f"{float(I_low):.6e}",
        }


# ============================================================
# 1. PURE TRANSFORMER STACK (no BitPerfectFilter)
# ============================================================
def zeros_matrix(rows, cols):
    return [[0.0 for _ in range(cols)] for _ in range(rows)]

def random_matrix(rows, cols):
    scale = math.sqrt(2.0 / cols)
    return [[random.gauss(0.0, scale) for _ in range(cols)] for _ in range(rows)]

def transpose(matrix):
    return [[matrix[r][c] for r in range(len(matrix))] for c in range(len(matrix[0]))]

def matmul(A, B):
    M, N = len(A), len(A[0])
    N2, P = len(B), len(B[0])
    assert N == N2, f"Dimension mismatch: {N} != {N2}"
    result = zeros_matrix(M, P)
    B_T = transpose(B)
    for i in range(M):
        for j in range(P):
            result[i][j] = sum(A[i][k] * B_T[j][k] for k in range(N))
    return result

def add_matrices(A, B):
    return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

def softmax_row_masked(row, mask_row=None):
    max_val = -float('inf')
    for i, val in enumerate(row):
        if mask_row and mask_row[i] == 1:
            continue
        if val > max_val:
            max_val = val
    if max_val == -float('inf'):
        max_val = 0.0
    exps = []
    for i, x in enumerate(row):
        if mask_row and mask_row[i] == 1:
            exps.append(0.0)
        else:
            exps.append(math.exp(x - max_val))
    sum_exps = sum(exps)
    if sum_exps == 0.0:
        return [1.0 / len(row) for _ in row]
    return [x / sum_exps for x in exps]


class LayerNorm:
    def __init__(self, d_model, eps=1e-5):
        self.eps = eps
        self.gamma = [1.0 for _ in range(d_model)]
        self.beta = [0.0 for _ in range(d_model)]

    def forward(self, X):
        N, D = len(X), len(X[0])
        out = zeros_matrix(N, D)
        for i in range(N):
            mean = sum(X[i]) / D
            variance = sum((x - mean) ** 2 for x in X[i]) / D
            std = math.sqrt(variance + self.eps)
            for j in range(D):
                out[i][j] = self.gamma[j] * ((X[i][j] - mean) / std) + self.beta[j]
        return out


class MultiHeadAttention:
    def __init__(self, d_model, n_heads):
        assert d_model % n_heads == 0
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        self.W_q = random_matrix(d_model, d_model)
        self.W_k = random_matrix(d_model, d_model)
        self.W_v = random_matrix(d_model, d_model)
        self.W_o = random_matrix(d_model, d_model)

    def forward(self, Q_in, K_in, V_in, is_causal=False):
        tgt_len = len(Q_in)
        src_len = len(K_in)
        Q_all = matmul(Q_in, transpose(self.W_q))
        K_all = matmul(K_in, transpose(self.W_k))
        V_all = matmul(V_in, transpose(self.W_v))
        head_outputs = []
        scale = math.sqrt(self.d_k)
        for h in range(self.n_heads):
            start_idx = h * self.d_k
            end_idx = start_idx + self.d_k
            Q_h = [[row[c] for c in range(start_idx, end_idx)] for row in Q_all]
            K_h = [[row[c] for c in range(start_idx, end_idx)] for row in K_all]
            V_h = [[row[c] for c in range(start_idx, end_idx)] for row in V_all]
            scores = matmul(Q_h, transpose(K_h))
            for i in range(tgt_len):
                mask_row = [1 if j > i else 0 for j in range(src_len)] if is_causal else None
                for j in range(src_len):
                    scores[i][j] /= scale
                scores[i] = softmax_row_masked(scores[i], mask_row)
            context_h = matmul(scores, V_h)
            head_outputs.append(context_h)
        concat_out = zeros_matrix(tgt_len, self.d_model)
        for i in range(tgt_len):
            col_idx = 0
            for h in range(self.n_heads):
                for j in range(self.d_k):
                    concat_out[i][col_idx] = head_outputs[h][i][j]
                    col_idx += 1
        return matmul(concat_out, transpose(self.W_o))


class PositionWiseFeedForward:
    def __init__(self, d_model, d_ff=None):
        if d_ff is None:
            d_ff = d_model * 4
        self.W1 = random_matrix(d_ff, d_model)
        self.W2 = random_matrix(d_model, d_ff)

    def forward(self, X):
        h1 = matmul(X, transpose(self.W1))
        for i in range(len(h1)):
            for j in range(len(h1[0])):
                if h1[i][j] < 0:
                    h1[i][j] = 0.0
        return matmul(h1, transpose(self.W2))


class EncoderLayer:
    def __init__(self, d_model, n_heads, d_ff=None):
        self.mha = MultiHeadAttention(d_model, n_heads)
        self.ffn = PositionWiseFeedForward(d_model, d_ff)
        self.norm1 = LayerNorm(d_model)
        self.norm2 = LayerNorm(d_model)

    def forward(self, X):
        attn_out = self.mha.forward(X, X, X, is_causal=False)
        x = self.norm1.forward(add_matrices(X, attn_out))
        ffn_out = self.ffn.forward(x)
        return self.norm2.forward(add_matrices(x, ffn_out))


class DecoderLayer:
    def __init__(self, d_model, n_heads, d_ff=None):
        self.self_attn = MultiHeadAttention(d_model, n_heads)
        self.cross_attn = MultiHeadAttention(d_model, n_heads)
        self.ffn = PositionWiseFeedForward(d_model, d_ff)
        self.norm1 = LayerNorm(d_model)
        self.norm2 = LayerNorm(d_model)
        self.norm3 = LayerNorm(d_model)

    def forward(self, tgt, memory):
        self_attn_out = self.self_attn.forward(tgt, tgt, tgt, is_causal=True)
        x = self.norm1.forward(add_matrices(tgt, self_attn_out))
        cross_attn_out = self.cross_attn.forward(x, memory, memory, is_causal=False)
        x = self.norm2.forward(add_matrices(x, cross_attn_out))
        ffn_out = self.ffn.forward(x)
        return self.norm3.forward(add_matrices(x, ffn_out))


class TransformerStack:
    def __init__(self, num_encoder_layers, num_decoder_layers, d_model, n_heads, d_ff=None):
        self.d_model = d_model
        self.encoder_layers = [EncoderLayer(d_model, n_heads, d_ff) for _ in range(num_encoder_layers)]
        self.decoder_layers = [DecoderLayer(d_model, n_heads, d_ff) for _ in range(num_decoder_layers)]

    def generate_positional_encoding(self, seq_len):
        pe = zeros_matrix(seq_len, self.d_model)
        for pos in range(seq_len):
            for i in range(0, self.d_model, 2):
                div_term = math.exp(i * -(math.log(10000.0) / self.d_model))
                pe[pos][i] = math.sin(pos * div_term)
                if i + 1 < self.d_model:
                    pe[pos][i + 1] = math.cos(pos * div_term)
        return pe

    def forward(self, src_tokens, tgt_tokens):
        src_pe = self.generate_positional_encoding(len(src_tokens))
        tgt_pe = self.generate_positional_encoding(len(tgt_tokens))
        enc_input = add_matrices(src_tokens, src_pe)
        dec_input = add_matrices(tgt_tokens, tgt_pe)
        memory = enc_input
        for layer in self.encoder_layers:
            memory = layer.forward(memory)
        output = dec_input
        for layer in self.decoder_layers:
            output = layer.forward(output, memory)
        return output


# ============================================================
# 2. STACCATO + TRANSFORMER PIPELINE (no BitPerfectFilter)
# ============================================================
class StaccatoTransformerPipeline:
    def __init__(self, 
                 num_encoder_layers=2, 
                 num_decoder_layers=2, 
                 d_model=64, 
                 n_heads=4):
        self.bridge = KernelDivisionBridge()
        self.staccato = LowCadenceVMM()
        self.transformer = TransformerStack(
            num_encoder_layers=num_encoder_layers,
            num_decoder_layers=num_decoder_layers,
            d_model=d_model,
            n_heads=n_heads
        )
        self.d_model = d_model

    def process(self, src_tokens, tgt_tokens):
        """
        Simple forward pass through the pure transformer stack.
        Staccato / kernel components remain available for later use.
        """
        output = self.transformer.forward(src_tokens, tgt_tokens)
        return {
            "transformer_output": output,
            "k_norm": self.bridge.k_norm_float,
            "staccato_gain": float(self.staccato.gain)
        }
