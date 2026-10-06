import math
from collections import Counter


class SentinelThreatEngine:
    @staticmethod
    def calculate_shannon_entropy(data: str) -> float:
        if not data:
            return 0.0
        entropy = 0.0
        freqs = Counter(data)
        length = len(data)
        for count in freqs.values():
            p_x = count / length
            entropy += - p_x * math.log2(p_x)
        return entropy

    def inspect_payload(self, payload: str) -> bool:
        """Returns True if the payload entropy is suspiciously high."""
        entropy = self.calculate_shannon_entropy(payload)
        # Threshold typically > 4.5 for generic json, > 5.0 for base64 encoded malicious scripts
        return entropy > 4.8
