import json
import re
from typing import List


class ContentFilter:
    def __init__(self, json_path: str, min_severity: int = 1):
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Verzeichnis, in dem ContentFilter.py liegt
        json_path_full = os.path.join(script_dir, json_path)
        self.patterns = self._load_patterns(json_path_full, min_severity)


    def _load_patterns(self, json_path: str, min_severity: int) -> List[str]:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        regex_patterns = []
        for category in data:
            if category.get("severity", 0) >= min_severity:
                for entry in category.get("dictionary", []):
                    regex_patterns.append(entry["match"])
        return regex_patterns

    def censor(self, text: str) -> str:
        # Funktion zum Ersetzen der Vokale in einem Wort durch '*'
        def censor_match(match):
            word = match.group(0)
            # Ersetze alle Vokale (a, e, i, o, u) durch "*"
            return ''.join('*' if c in 'aeiouAEIOU' else c for c in word)

        censored_text = text
        for pattern in self.patterns:
            censored_text = re.sub(pattern, censor_match, censored_text, flags=re.IGNORECASE)
        return censored_text
