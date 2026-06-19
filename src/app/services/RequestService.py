from app.domain.ApprovalPolicy import ApprovalPolicy
from app.domain.PurchaseRequest import (
    ApprovalLevel,
    Decision,
    PurchaseRequest,
    RequestStatus,
)
from app.utils.Logger import Logger


class RequestService:
    """Orkiestracja przepływu: rejestracja, ruting akceptacji, decyzja, audyt.

    Spina warstwy (policy, repozytorium, powiadomienia, archiwum) — odpowiednik
    funkcji-handlera, ale w testowalnej formie klasy.
    """

    def __init__(self, repository, notifier, archive, policy: ApprovalPolicy = None):
        self.log = Logger.get()
        self.repo = repository
        self.notifier = notifier
        self.archive = archive
        self.policy = policy or ApprovalPolicy()

    def submit(self, request: PurchaseRequest) -> PurchaseRequest:
        """Kroki 1–2: rejestruje wniosek i wyznacza ścieżkę akceptacji."""
        route = self.policy.evaluate(request.amount, request.currency)
        request.request_id = self.repo.save(request)
        self.archive.append("RequestSubmitted", request)

        if route.auto_approve:
            self.log.info("Wniosek %s — automatyczna akceptacja.", request.request_id)
            return self._finalize(request, RequestStatus.AUTO_APPROVED)

        self.notifier.publish(
            "ApprovalRequired",
            {"request_id": request.request_id, "required_level": route.required_level.value},
        )
        self.log.info("Wniosek %s oczekuje na akceptację: %s", request.request_id, route.required_level.value)
        return request

    def decide(
        self,
        request: PurchaseRequest,
        decision: Decision,
        approver_level: ApprovalLevel,
    ) -> PurchaseRequest:
        """Krok 3: rejestruje decyzję akceptującego i finalizuje wniosek."""
        route = self.policy.evaluate(request.amount, request.currency)

        # Egzekwowanie reguły progu niezależnie od UI — wniosek > progu
        # wymaga bezwzględnej akceptacji Dyrektora Działu.
        if route.required_level == ApprovalLevel.DIRECTOR and approver_level != ApprovalLevel.DIRECTOR:
            raise PermissionError("Wniosek powyżej progu wymaga akceptacji Dyrektora Działu.")

        status = RequestStatus.APPROVED if decision == Decision.APPROVE else RequestStatus.REJECTED
        return self._finalize(request, status)

    def _finalize(self, request: PurchaseRequest, status: RequestStatus) -> PurchaseRequest:
        """Kroki 4–5: zapis statusu, niezmienny audyt, powiadomienie zwrotne."""
        request.status = status
        self.repo.update_status(request.request_id, status)
        self.archive.append(status.value, request)
        self.notifier.notify_requester(request.request_id, status.value)
        return request
