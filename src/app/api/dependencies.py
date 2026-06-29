import os

from fastapi import Header, HTTPException

from app.domain.PurchaseRequest import ApprovalLevel, PurchaseRequest
from app.services.RequestService import RequestService
from app.utils.Logger import Logger

log = Logger.get()


def get_service() -> RequestService:
    """Builds RequestService with cloud dependencies.

    In Azure, connections (SQL, Service Bus, Blob) are created with
    ``DefaultAzureCredential`` (Managed Identity) — no secrets in code.
    This DI hook keeps domain logic testable locally.
    """
    from app.infra.factory import build_request_service  # lazy cloud infra import

    return build_request_service()


def get_request(request_id: int, service: RequestService = None) -> PurchaseRequest:
    """Loads request from repository (simplified for this example)."""
    service = service or get_service()
    request = service.repo.get(request_id) if hasattr(service.repo, "get") else None
    if request is None:
        raise HTTPException(status_code=404, detail="Request not found.")
    return request


def require_approver(x_ms_client_roles: str = Header(default="")) -> ApprovalLevel:
    """Maps Entra ID token roles to approval level.

    Header comes from JWT validation in API Management / Easy Auth.
    """
    roles = {r.strip() for r in x_ms_client_roles.split(",") if r.strip()}
    if "Director" in roles:
        return ApprovalLevel.DIRECTOR
    if "Manager" in roles:
        return ApprovalLevel.MANAGER
    raise HTTPException(status_code=403, detail="Insufficient permissions to approve requests.")
