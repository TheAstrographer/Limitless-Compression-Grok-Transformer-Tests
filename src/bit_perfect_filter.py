import hashlib
import re
from collections import defaultdict
from typing import Dict

class BitPerfectFilter:
    UNIT_SEP = '\x1F'
    GROUP_SEP = '\x1D'

    def __init__(self, max_units: int = 80, max_length: int = 8000):
        self.max_units = max_units
        self.max_length = max_length
        self.session_counters = defaultdict(lambda: defaultdict(int))
        self.CACHE_4: Dict[str, str] = {}
        self.marker_pattern = re.compile(r'\[([A-Za-z0-9_-]{1,20})\]')

    def _collapse_blocks(self, text: str) -> str:
        if not text:
            return ""
        if len(text) > self.max_length:
            return self.GROUP_SEP
        cleaned = self.marker_pattern.sub(self.UNIT_SEP, text)
        cleaned = re.sub(r'[\s]+', ' ', cleaned).strip()
        units = re.split(r'([{};\n])', cleaned)
        cleaned_units = [u.strip() for u in units if u.strip()]
        collapsed = self.UNIT_SEP.join(cleaned_units)
        unit_count = collapsed.count(self.UNIT_SEP)
        if unit_count >= self.max_units or len(collapsed) > self.max_length:
            return self.GROUP_SEP
        if unit_count >= 2:
            return self.GROUP_SEP + collapsed + self.GROUP_SEP
        return collapsed

    def filter_message(self, text: str, session_id: str = "default"):
        original = text
        collapsed = self._collapse_blocks(text)
        block_hash = hashlib.sha256(collapsed.encode('utf-8', errors='ignore')).hexdigest()[:32]
        counter = self.session_counters[session_id]
        counter[block_hash] += 1
        is_first = counter[block_hash] == 1
        if is_first:
            self.CACHE_4[block_hash] = original
        return {
            "block_hash": block_hash,
            "original_len": len(original),
            "collapsed_len": len(collapsed),
            "is_suppressed": collapsed == self.GROUP_SEP,
            "unit_count": collapsed.count(self.UNIT_SEP) if collapsed != self.GROUP_SEP else 0,
            "is_first_occurrence": is_first,
            "occurrence_count": counter[block_hash],
            "extractable": True,
            "collapsed_text": collapsed
        }

    def extract_original(self, block_hash: str) -> str:
        return self.CACHE_4.get(block_hash, "")
