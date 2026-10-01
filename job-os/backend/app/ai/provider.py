from typing import Protocol


class AIProvider(Protocol):
    def complete(self, *, system: str, user: str) -> str:
        """Return the model text for a system/user prompt pair."""
