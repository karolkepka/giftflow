# GiftFlow — gift and reward purchase workflow engine

Reference pro-code implementation of the core for the gift/reward purchase workflow scenario. **FastAPI** backend running serverless on **Azure Functions**, data in **Azure SQL** (3NF), events via **Service Bus**, immutable archive in **Blob (WORM)**.

## Structure (OOP — one class per file)

```
app/
  api/
    main.py            # FastAPI: POST /requests, POST /requests/{id}/decision
    dependencies.py    # DI + Entra ID role mapping -> approval level
  domain/
    PurchaseRequest.py # entity + enums (status, level, decision)
    ApprovalPolicy.py  # deterministic 1000 PLN threshold rule
  services/
    RequestService.py      # workflow orchestration (steps 1-5)
    NotificationService.py # event publishing + feedback (Service Bus)
    AuditArchive.py        # immutable audit write (Blob WORM)
  repositories/
    RequestRepository.py   # Azure SQL (Managed Identity)
  infra/
    factory.py             # Azure SDK binding (DefaultAzureCredential)
  utils/
    Logger.py              # Logger.get() — shared logger
tests/
  test_approval_policy.py  # threshold rule verification (determinism)
```

## Design principles

- **No secrets in code** — `DefaultAzureCredential` (Managed Identity) + Key Vault.
- **Deterministic, testable threshold rule** — no GenAI in the decision path.
- **Layer separation** — domain independent of cloud SDK (easy tests and mocks).

## Running tests

```bash
pip install -r requirements.txt
PYTHONPATH=. pytest -q
```
