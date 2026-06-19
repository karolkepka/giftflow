import os
from dataclasses import dataclass
from decimal import Decimal

from app.domain.PurchaseRequest import ApprovalLevel
from app.utils.Logger import Logger


@dataclass(frozen=True)
class ApprovalRoute:
    """Wynik ewaluacji reguły progu — wymagany poziom akceptacji."""

    required_level: ApprovalLevel
    auto_approve: bool
    reason: str


class ApprovalPolicy:
    """Deterministyczna reguła progu akceptacji (domyślnie 1000 PLN).

    Próg jest konfigurowalny zmienną środowiskową, ale sama decyzja pozostaje
    w pełni deterministyczna i audytowalna — celowo bez GenAI w torze decyzyjnym.
    """

    def __init__(self):
        self.log = Logger.get()
        self.config = {
            "THRESHOLD_PLN": Decimal(os.getenv("APPROVAL_THRESHOLD_PLN", "1000")),
            "AUTO_APPROVE_BELOW_THRESHOLD": os.getenv("AUTO_APPROVE", "True") == "True",
        }

    def evaluate(self, amount: Decimal, currency: str = "PLN") -> ApprovalRoute:
        """Zwraca wymaganą ścieżkę akceptacji dla danej kwoty wniosku."""
        if currency != "PLN":
            raise ValueError(f"Nieobsługiwana waluta: {currency}")
        if amount <= 0:
            raise ValueError("Kwota wniosku musi być dodatnia.")

        threshold = self.config["THRESHOLD_PLN"]

        if amount > threshold:
            self.log.info("Kwota %s > %s PLN — wymagana akceptacja Dyrektora.", amount, threshold)
            return ApprovalRoute(ApprovalLevel.DIRECTOR, False, "Powyżej progu — Dyrektor Działu")

        if self.config["AUTO_APPROVE_BELOW_THRESHOLD"]:
            return ApprovalRoute(ApprovalLevel.AUTO, True, "Na/poniżej progu — automatyczna akceptacja")

        return ApprovalRoute(ApprovalLevel.MANAGER, False, "Na/poniżej progu — akceptacja przełożonego")
