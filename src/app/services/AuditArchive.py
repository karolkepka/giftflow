import json
import os
from dataclasses import asdict

from app.utils.Logger import Logger


class AuditArchive:
    """Immutable (WORM) audit event writes to secure cloud archive.

    Blob container configured with immutability policy — ``overwrite=False``
    guarantees existing audit trail cannot be overwritten.
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
        self.log.info("Archiving audit event: %s", blob_path)
        self.container.upload_blob(blob_path, json.dumps(record, default=str), overwrite=False)


def _to_dict(request) -> dict:
    try:
        return asdict(request)
    except TypeError:
        return dict(request.__dict__)
