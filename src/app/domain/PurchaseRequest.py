from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional


class RequestStatus(str, Enum):
    PENDING = "PENDING"
    AUTO_APPROVED = "AUTO_APPROVED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ApprovalLevel(str, Enum):
    AUTO = "AUTO"
    MANAGER = "MANAGER"
    DIRECTOR = "DIRECTOR"


class Decision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"


@dataclass
class PurchaseRequest:
    """Gift/reward purchase request — domain entity (maps to 3NF table)."""

    employee_id: int
    beneficiary_id: int
    gift_type_id: int
    purpose: str
    amount: Decimal
    currency: str = "PLN"
    request_id: Optional[int] = None
    status: RequestStatus = RequestStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def is_open(self) -> bool:
        return self.status == RequestStatus.PENDING
