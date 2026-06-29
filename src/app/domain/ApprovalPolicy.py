import os
from dataclasses import dataclass
from decimal import Decimal

from app.domain.PurchaseRequest import ApprovalLevel
from app.utils.Logger import Logger


@dataclass(frozen=True)
class ApprovalRoute:
    """Result of threshold rule evaluation — required approval level."""

    required_level: ApprovalLevel
    auto_approve: bool
    reason: str


class ApprovalPolicy:
    """Deterministic approval threshold rule (default 1000 PLN).

    The threshold is configurable via environment variable, but the decision
    remains fully deterministic and auditable — intentionally no GenAI on the decision path.
    """

    def __init__(self):
        self.log = Logger.get()
        self.config = {
            "THRESHOLD_PLN": Decimal(os.getenv("APPROVAL_THRESHOLD_PLN", "1000")),
            "AUTO_APPROVE_BELOW_THRESHOLD": os.getenv("AUTO_APPROVE", "True") == "True",
        }

    def evaluate(self, amount: Decimal, currency: str = "PLN") -> ApprovalRoute:
        """Returns the required approval path for the given request amount."""
        if currency != "PLN":
            raise ValueError(f"Unsupported currency: {currency}")
        if amount <= 0:
            raise ValueError("Request amount must be positive.")

        threshold = self.config["THRESHOLD_PLN"]

        if amount > threshold:
            self.log.info("Amount %s > %s PLN — Director approval required.", amount, threshold)
            return ApprovalRoute(ApprovalLevel.DIRECTOR, False, "Above threshold — Department Director")

        if self.config["AUTO_APPROVE_BELOW_THRESHOLD"]:
            return ApprovalRoute(ApprovalLevel.AUTO, True, "At/below threshold — auto-approval")

        return ApprovalRoute(ApprovalLevel.MANAGER, False, "At/below threshold — supervisor approval")
