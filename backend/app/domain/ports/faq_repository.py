from typing import List, Protocol

from app.domain.entities.faq import FaqEntry


class FaqRepository(Protocol):
    def list_entries(self) -> List[FaqEntry]:
        ...
