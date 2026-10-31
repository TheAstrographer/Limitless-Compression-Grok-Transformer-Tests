"""
arcan_jcrin_helpers.py

Helper logic utilizing:
- https://github.com/TheAstrographer/The-First-Ever-Softmax-Temperature-Spherical-Attention-Map
- https://github.com/TheAstrographer/The-Tanarcantau-Shannon-Entropy-JCRIN-Definitive-Infinity
- https://github.com/TheAstrographer/JCRIN-Radial-Emergence

This module provides clean, reusable functions for:
- Temperature schedule τ(λ) = 2π(1-λ)
- Spherical / radial inspired probability maps
- Shannon entropy
- Basic JCRIN-style capacity factors
"""

import math
from typing import List

# Core constants drawn from the JCRIN / Arcan materials
PSI = 0.15033788                  # ≈ 8.61°
COS_PSI = math.cos(PSI)           # ≈ 0.98872053
COS2_PSI = COS_PSI ** 2           # ≈ 0.9775 (97.75%)
ETA_PSI = PSI / (2 * math.pi)     # ≈ 0.02392
M = 30

def tau_from_lambda(lam: float) -> float:
    """
    Temperature schedule from the spherical attention framework:
    τ(λ) = 2π (1 - λ)
    """
    return 2 * math.pi * (1.0 - lam)

def shannon_entropy(probs: List[float]) -> float:
    """
    Shannon entropy H(P) = -Σ p log p
    (from The-Tanarcantau-Shannon-Entropy repository ideas)
    """
    h = 0.0
    for p in probs:
        if p > 0.0:
            h -= p * math.log(p)
    return h

def get_angles(N: int) -> List[float]:
    """Discrete angles t_k = 2π k / N"""
    return [2 * math.pi * k / N for k in range(N)]

def compute_P(N: int, cos_psi: float = COS_PSI) -> List[float]:
    """
    Probability distribution used in the JCRIN materials:
    P_i = exp(cos(t_i) * cosψ) / Σ exp(cos(t_j) * cosψ)
    """
    angles = get_angles(N)
    logits = [math.exp(math.cos(t) * cos_psi) for t in angles]
    Z = sum(logits)
    return [x / Z for x in logits]

def compute_A(N: int, cos2_psi: float = COS2_PSI) -> List[float]:
    """
    Alternative form:
    A_i related to exp(cos(t_i) * cos²ψ)
    """
    angles = get_angles(N)
    logits = [math.exp(math.cos(t) * cos2_psi) for t in angles]
    Z = sum(logits)
    return [x / Z for x in logits]

def jcrin_capacity_factor() -> float:
    """Simple retention / capacity factor (cos²ψ ≈ 0.9775)"""
    return COS2_PSI

def effective_B(U: float) -> float:
    """B_effective ≈ (M * ηψ) * U"""

    return (M * ETA_PSI) * U
