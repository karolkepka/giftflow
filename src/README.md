# GiftFlow — silnik workflow zakupu prezentów i nagród

Referencyjna implementacja rdzenia pro-code dla scenariusza obiegu zakupów
prezentów/nagród. Backend **FastAPI** uruchamiany serverless na **Azure Functions**,
dane w **Azure SQL** (3NF), zdarzenia przez **Service Bus**, niezmienne archiwum
w **Blob (WORM)**.

## Struktura (OOP — jedna klasa na plik)

```
app/
  api/
    main.py            # FastAPI: POST /requests, POST /requests/{id}/decision
    dependencies.py    # DI + mapowanie ról Entra ID -> poziom akceptacji
  domain/
    PurchaseRequest.py # encja + enumy (status, poziom, decyzja)
    ApprovalPolicy.py  # deterministyczna reguła progu 1000 PLN
  services/
    RequestService.py      # orkiestracja przepływu (kroki 1-5)
    NotificationService.py # publikacja zdarzeń + feedback (Service Bus)
    AuditArchive.py        # niezmienny zapis audytu (Blob WORM)
  repositories/
    RequestRepository.py   # Azure SQL (Managed Identity)
  infra/
    factory.py             # wiązanie z SDK Azure (DefaultAzureCredential)
  utils/
    Logger.py              # Logger.get() — współdzielony logger
tests/
  test_approval_policy.py  # weryfikacja reguły progu (determinizm)
```

## Zasady projektowe

- **Brak sekretów w kodzie** — `DefaultAzureCredential` (Managed Identity) + Key Vault.
- **Reguła progu deterministyczna i testowalna** — bez GenAI w torze decyzyjnym.
- **Separacja warstw** — domena niezależna od SDK chmury (łatwe testy i mocki).

## Uruchomienie testów

```bash
pip install -r requirements.txt
PYTHONPATH=. pytest -q
```
