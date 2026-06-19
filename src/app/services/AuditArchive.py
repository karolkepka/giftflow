import json
import os
from dataclasses import asdict

from app.utils.Logger import Logger


class AuditArchive:
    """Niezmienny (WORM) zapis zdarzeń audytu do bezpiecznego archiwum chmurowego.

    Kontener Blob skonfigurowany z polityką immutability — ``overwrite=False``
    gwarantuje brak nadpisań istniejącego śladu audytowego.
    """

    def __init__(self, blob_container):
        self.log = Logger.get()
        self.container = blob_container
        self.config = {
            "PREFIX": os.getenv("AUDIT_PREFIX", "audit"),
        }

    def append(self, event_type: str, request) -> None:
        record = {"event": event_type, "request": _to_dict(request)}
        blob_path = f"{self.config['PREFIX']}/{request.request_id}/{event_type}.json"
        self.log.info("Archiwizacja audytu: %s", blob_path)
        self.container.upload_blob(blob_path, json.dumps(record, default=str), overwrite=False)


def _to_dict(request) -> dict:
    try:
        return asdict(request)
    except TypeError:
        return dict(request.__dict__)
