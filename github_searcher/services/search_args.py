from datetime import date
from dataclasses import dataclass


@dataclass
class SearchArgs:
    """
    Simple structure for storing searching parameters.
    Could be extended.
    """
    created_from: date | None
    lang: str | None
    page_id: int = 0

    def __str__(self):
        return f"{self.created_from};{self.lang};{self.page_id}"
