import json
import os

from app.utils.Logger import Logger


class NotificationService:
    """Publishes events to Azure Service Bus and triggers feedback notification.

    Sender comes from ``azure-servicebus`` and is authenticated via Managed Identity.
    """

    def __init__(self, sender):
        self.log = Logger.get()
        self.sender = sender
        self.config = {
            "TOPIC": os.getenv("SB_TOPIC", "request-events"),
        }

    def publish(self, event_type: str, payload: dict) -> None:
        message = {"event": event_type, "payload": payload}
        self.log.info("Publishing event: %s -> %s", event_type, self.config["TOPIC"])
        self.sender.send_messages(json.dumps(message, default=str))

    def notify_requester(self, request_id: int, decision: str) -> None:
        """Scenario step 3 — automatic feedback to the requester."""
        self.publish("RequestDecided", {"request_id": request_id, "decision": decision})
