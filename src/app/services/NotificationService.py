import json
import os

from app.utils.Logger import Logger


class NotificationService:
    """Publikuje zdarzenia do Azure Service Bus i wyzwala powiadomienie zwrotne.

    Sender pochodzi z ``azure-servicebus`` i jest uwierzytelniany Managed Identity.
    """

    def __init__(self, sender):
        self.log = Logger.get()
        self.sender = sender
        self.config = {
            "TOPIC": os.getenv("SB_TOPIC", "request-events"),
        }

    def publish(self, event_type: str, payload: dict) -> None:
        message = {"event": event_type, "payload": payload}
        self.log.info("Publikacja zdarzenia: %s -> %s", event_type, self.config["TOPIC"])
        self.sender.send_messages(json.dumps(message, default=str))

    def notify_requester(self, request_id: int, decision: str) -> None:
        """Krok 3 scenariusza — automatyczny feedback do wnioskodawcy."""
        self.publish("RequestDecided", {"request_id": request_id, "decision": decision})
