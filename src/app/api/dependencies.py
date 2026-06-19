import os

from fastapi import Header, HTTPException

from app.domain.PurchaseRequest import ApprovalLevel, PurchaseRequest
from app.services.RequestService import RequestService
from app.utils.Logger import Logger

log = Logger.get()


def get_service() -> RequestService:
    """Buduje RequestService z zależnościami chmurowymi.

    W środowisku Azure połączenia (SQL, Service Bus, Blob) są tworzone z
    ``DefaultAzureCredential`` (Managed Identity) — bez sekretów w kodzie.
    Tu zostawiamy punkt wstrzyknięcia (DI), aby logikę dało się testować lokalnie.
    """
    from app.infra.factory import build_request_service  # leniwy import infry chmurowej

    return build_request_service()


def get_request(request_id: int, service: RequestService = None) -> PurchaseRequest:
    """Pobiera wniosek z repozytorium (uproszczone na potrzeby przykładu)."""
    service = service or get_service()
    request = service.repo.get(request_id) if hasattr(service.repo, "get") else None
    if request is None:
        raise HTTPException(status_code=404, detail="Wniosek nie istnieje.")
    return request


def require_approver(x_ms_client_roles: str = Header(default="")) -> ApprovalLevel:
    """Mapuje role z tokenu Entra ID na poziom akceptacji.

    Nagłówek pochodzi z walidacji JWT w API Management / Easy Auth.
    """
    roles = {r.strip() for r in x_ms_client_roles.split(",") if r.strip()}
    if "Director" in roles:
        return ApprovalLevel.DIRECTOR
    if "Manager" in roles:
        return ApprovalLevel.MANAGER
    raise HTTPException(status_code=403, detail="Brak uprawnień do akceptacji wniosków.")
