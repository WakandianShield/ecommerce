from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class FaqEntry:
    id: str
    question: str
    answer: str
    keywords: List[str]
