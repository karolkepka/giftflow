from app.domain.ApprovalPolicy import ApprovalPolicy
from app.domain.PurchaseRequest import (
    ApprovalLevel,
    Decision,
    PurchaseRequest,
    RequestStatus,
)
from app.utils.Logger import Logger


class RequestService:
    """Workflow orchestration: registration, approval routing, decision, audit.

    Wires layers (policy, repository, notifications, archive) — equivalent to a
    function handler, but in a testable class form.
    """

    def __init__(self, repository, notifier, archive, policy: ApprovalPolicy = None):
        self.log = Logger.get()
        self.repo = repository
        self.notifier = notifier
        self.archive = archive
        self.policy = policy or ApprovalPolicy()

    def submit(self, request: PurchaseRequest) -> PurchaseRequest:
        """Steps 1–2: register request and determine approval path."""
        route = self.policy.evaluate(request.amount, request.currency)
        request.request_id = self.repo.save(request)
        self.archive.append("RequestSubmitted", request)

        if route.auto_approve:
            self.log.info("Request %s — auto-approved.", request.request_id)
            return self._finalize(request, RequestStatus.AUTO_APPROVED)

        self.notifier.publish(
            "ApprovalRequired",
            {"request_id": request.request_id, "required_level": route.required_level.value},
        )
        self.log.info("Request %s awaiting approval: %s", request.request_id, route.required_level.value)
        return request

    def decide(
        self,
        request: PurchaseRequest,
        decision: Decision,
        approver_level: ApprovalLevel,
    ) -> PurchaseRequest:
        """Step 3: record approver decision and finalize request."""
        route = self.policy.evaluate(request.amount, request.currency)

        # Enforce threshold rule independent of UI — requests above threshold
        # require mandatory Department Director approval.
        if route.required_level == ApprovalLevel.DIRECTOR and approver_level != ApprovalLevel.DIRECTOR:
            raise PermissionError("Requests above threshold require Department Director approval.")

        status = RequestStatus.APPROVED if decision == Decision.APPROVE else RequestStatus.REJECTED
        return self._finalize(request, status)

    def _finalize(self, request: PurchaseRequest, status: RequestStatus) -> PurchaseRequest:
        """Steps 4–5: persist status, immutable audit, feedback notification."""
        request.status = status
        self.repo.update_status(request.request_id, status)
        self.archive.append(status.value, request)
        self.notifier.notify_requester(request.request_id, status.value)
        return request
