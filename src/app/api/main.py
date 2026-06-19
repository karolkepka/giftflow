from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException

from pydantic import BaseModel, Field

from app.api.dependencies import get_request, get_service, require_approver
from app.domain.PurchaseRequest import ApprovalLevel, Decision, PurchaseRequest
from app.services.RequestService import RequestService
from app.utils.Logger import Logger

log = Logger.get()

app = FastAPI(title="GiftFlow API", version="1.0", description="Workflow zakupu prezentów i nagród")


class RequestIn(BaseModel):
    employee_id: int
    beneficiary_id: int
    gift_type_id: int
    purpose: str = Field(min_length=3, max_length=500)
    amount: Decimal = Field(gt=0)
    currency: str = "PLN"


class DecisionIn(BaseModel):
    decision: Decision


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/requests", status_code=201)
def create_request(body: RequestIn, service: RequestService = Depends(get_service)) -> dict:
    """Krok 1–2: rejestracja wniosku i automatyczny ruting akceptacji."""
    request = PurchaseRequest(**body.model_dump())
    result = service.submit(request)
    return {"request_id": result.request_id, "status": result.status.value}


@app.post("/requests/{request_id}/decision")
def decide_request(
    request_id: int,
    body: DecisionIn,
    approver_level: ApprovalLevel = Depends(require_approver),
    request: PurchaseRequest = Depends(get_request),
    service: RequestService = Depends(get_service),
) -> dict:
    """Krok 3: decyzja przełożonego/Dyrektora (poziom z claimu JWT Entra ID)."""
    try:
        result = service.decide(request, body.decision, approver_level)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    return {"request_id": result.request_id, "status": result.status.value}
