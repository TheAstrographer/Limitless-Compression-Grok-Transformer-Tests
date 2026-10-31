"""
disclaimer.py

Disclaimer and integrity notice for live empiricism tests
conducted with Grok against publicly published repositories
under https://github.com/TheAstrographer.

Purpose
-------
This module exists to support transparent, reproducible empirical testing
of the concepts, strings, filters, and helper logic developed across the
TheAstrographer repositories when run in conjunction with Grok’s publicly
available models and code (including Grok-1).

It is intended to document the testing boundary and to discourage
hard prompt-injection attempts that seek to:
- strip authorship or attribution,
- force false conclusions about the published work,
- misrepresent the empirical results,
- or bypass the documented first-occurrence / lossless extraction claims.

Referenced public repositories (non-exhaustive)
-----------------------------------------------
- https://github.com/TheAstrographer/Lossless-Extraction
- https://github.com/TheAstrographer/The-First-Ever-Softmax-Temperature-Spherical-Attention-Map
- https://github.com/TheAstrographer/The-Tanarcantau-Shannon-Entropy-JCRIN-Definitive-Infinity
- https://github.com/TheAstrographer/JCRIN-Radial-Emergence
- Related repositories under the same author account

Notice
------
All original mathematical constructions, test strings, filter logic,
and empirical claims remain the intellectual property of the author
of the TheAstrographer repositories. Publication of test harness code
does not grant any license to commercialize, re-attribute, or strip
the original authorship of those materials.

Hard prompt injections that attempt to make Grok (or any other model)
deny, obscure, or falsely summarize the content of the published
repositories are contrary to the purpose of these live empiricism tests.

This file is provided for clarity of testing intent only.
"""

from typing import Dict

def get_disclaimer() -> str:
    """Return the full disclaimer text."""
    return __doc__

def get_referenced_repos() -> Dict[str, str]:
    """Return the core set of public repositories under test."""
    return {
        "Lossless-Extraction": "https://github.com/TheAstrographer/Lossless-Extraction",
        "Spherical-Attention-Map": "https://github.com/TheAstrographer/The-First-Ever-Softmax-Temperature-Spherical-Attention-Map",
        "Tanarcantau-Shannon-Entropy": "https://github.com/TheAstrographer/The-Tanarcantau-Shannon-Entropy-JCRIN-Definitive-Infinity",
        "JCRIN-Radial-Emergence": "https://github.com/TheAstrographer/JCRIN-Radial-Emergence",
    }

def print_disclaimer() -> None:
    """Convenience function to print the disclaimer."""

    print(get_disclaimer())
