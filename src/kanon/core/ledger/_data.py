from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from kanon.core.config import Integration
from kanon.core.ledger._models import IntegrationLedger

LEDGER_FILE = "ledger.json"

Progress = Callable[[str], None] | None


class LedgerData(BaseModel):
    """The ledger contents and the file they live in; shared base of the Ledger mixins."""

    model_config = ConfigDict(extra="forbid")

    path: Path = Field(exclude=True)
    integrations: dict[Integration, IntegrationLedger] = Field(default_factory=dict)

    def integration_ledger(self, integration: Integration) -> IntegrationLedger:
        return self.integrations.setdefault(integration, IntegrationLedger())

    def prune(self, integration: Integration) -> None:
        """Drop `name` if nothing is recorded for it."""
        entry = self.integrations.get(integration)
        if entry is not None and entry.is_empty():
            del self.integrations[integration]
