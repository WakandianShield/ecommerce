from typing import List, Optional, Protocol

from app.domain.entities.faq import FaqEntry


class FaqMatcher(Protocol):
    def match(self, text: str, entries: List[FaqEntry]) -> Optional[FaqEntry]:
        ...
