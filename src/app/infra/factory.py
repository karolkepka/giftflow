import os

from app.repositories.RequestRepository import RequestRepository
from app.services.AuditArchive import AuditArchive
from app.services.NotificationService import NotificationService
from app.services.RequestService import RequestService
from app.utils.Logger import Logger

log = Logger.get()


def build_request_service() -> RequestService:
    """Assembles RequestService from Azure clients authenticated via Managed Identity.

    All credentials come from ``DefaultAzureCredential`` + Key Vault —
    no secrets in code. This is the only place binding domain logic to the
    cloud SDK, which keeps unit tests easy (mocks).
    """
    from azure.identity import DefaultAzureCredential
    from azure.servicebus import ServiceBusClient
    from azure.storage.blob import BlobServiceClient
    import pyodbc

    credential = DefaultAzureCredential()

    sql_conn = pyodbc.connect(os.environ["SQL_CONNECTION_STRING"], attrs_before={1256: credential})
    repo = RequestRepository(sql_conn)

    sb_client = ServiceBusClient(os.environ["SERVICE_BUS_FQDN"], credential)
    sender = sb_client.get_topic_sender(os.getenv("SB_TOPIC", "request-events"))
    notifier = NotificationService(sender)

    blob = BlobServiceClient(os.environ["BLOB_ACCOUNT_URL"], credential)
    container = blob.get_container_client(os.getenv("AUDIT_CONTAINER", "audit-archive"))
    archive = AuditArchive(container)

    return RequestService(repository=repo, notifier=notifier, archive=archive)
