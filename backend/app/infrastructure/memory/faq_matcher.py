import re
import unicodedata
from typing import List, Optional

from app.domain.entities.faq import FaqEntry


class SimpleFaqMatcher:
    def match(self, text: str, entries: List[FaqEntry]) -> Optional[FaqEntry]:
        normalized = _normalize(text)
        best_entry: Optional[FaqEntry] = None
        best_score = 0
        for entry in entries:
            score = 0
            for keyword in entry.keywords:
                if keyword in normalized:
                    score += 1
            if score > best_score:
                best_score = score
                best_entry = entry
        if best_score == 0:
            return None
        return best_entry


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text.lower()
    ascii_text = re.sub(r"[^a-z0-9\s]", " ", ascii_text)
    return " ".join(ascii_text.split())
