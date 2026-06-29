import os

from app.domain.PurchaseRequest import PurchaseRequest, RequestStatus
from app.utils.Logger import Logger


class RequestRepository:
    """Azure SQL access (3NF model).

    Connection authenticated via Managed Identity — no passwords in code;
    connection parameters read from Key Vault.
    """

    def __init__(self, connection):
        self.log = Logger.get()
        self.conn = connection
        self.config = {
            "TABLE": os.getenv("REQUEST_TABLE", "dbo.purchase_request"),
        }

    def save(self, request: PurchaseRequest) -> int:
        self.log.info("Saving request: %s", request.purpose)
        cursor = self.conn.cursor()
        cursor.execute(
            f"INSERT INTO {self.config['TABLE']} "
            "(employee_id, beneficiary_id, gift_type_id, purpose, amount, currency, status) "
            "OUTPUT INSERTED.request_id "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            request.employee_id,
            request.beneficiary_id,
            request.gift_type_id,
            request.purpose,
            request.amount,
            request.currency,
            request.status.value,
        )
        request.request_id = int(cursor.fetchone()[0])
        self.conn.commit()
        return request.request_id

    def get(self, request_id: int) -> PurchaseRequest:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT employee_id, beneficiary_id, gift_type_id, purpose, amount, currency, "
            "request_id, status "
            f"FROM {self.config['TABLE']} WHERE request_id = ?",
            request_id,
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return PurchaseRequest(
            employee_id=row[0],
            beneficiary_id=row[1],
            gift_type_id=row[2],
            purpose=row[3],
            amount=row[4],
            currency=row[5],
            request_id=row[6],
            status=RequestStatus(row[7]),
        )

    def update_status(self, request_id: int, status: RequestStatus) -> None:
        self.log.info("Updating request %s status -> %s", request_id, status.value)
        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE {self.config['TABLE']} "
            "SET status = ?, updated_at = SYSUTCDATETIME() "
            "WHERE request_id = ?",
            status.value,
            request_id,
        )
        self.conn.commit()
