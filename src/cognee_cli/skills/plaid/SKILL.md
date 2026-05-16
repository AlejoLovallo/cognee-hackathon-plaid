---
name: plaid
description: Use the official Plaid Python package to call Plaid APIs from Python. Trigger this skill when implementing or debugging Plaid integrations, installing plaid-python, configuring Sandbox/Development/Production clients, creating Link tokens, exchanging public tokens, fetching accounts, balances, transactions, identity, auth, liabilities, investments, handling Plaid ApiException errors, serializing generated model responses, or consulting Plaid's OpenAPI-generated request/response models.
---

# Plaid Python API Calls

Use the official `plaid-python` package for Plaid API calls. It is generated from Plaid's OpenAPI spec, so endpoint calls use typed request classes from `plaid.model.*` and a `PlaidApi` client from `plaid.api.plaid_api`.

Primary references:

- Plaid OpenAPI spec: https://github.com/plaid/plaid-openapi
- Python client: https://github.com/plaid/plaid-python
- PyPI package: https://pypi.org/project/plaid-python/
- Plaid API docs: https://plaid.com/docs/api/

Bundled references:

- `references/data-and-openapi.md`: local guide for the bundled OpenAPI spec and sample payloads. Read this before implementing product-specific calls or tests.
- `data/api_def.yml`: full local Plaid OpenAPI definition. Search it with `rg`; do not load it wholesale into context.
- `data/Auth.json`, `data/Balance.json`, `data/Identity.json`, `data/Transactions.json`, `data/Assets_Report.json`: sample responses for fixtures and response-shape checks.

## Setup

Ensure the project depends on the PyPI package:

```bash
uv add plaid-python
```

Use environment variables. Do not hard-code Plaid credentials or access tokens.

```bash
PLAID_CLIENT_ID=
PLAID_SECRET=
PLAID_ENV=sandbox
```

Accept these environment names: `sandbox`, `development`, `production`. Default local examples to `sandbox`.

## Client Factory

Create one small factory and reuse it. Avoid scattering Plaid configuration across command handlers.

```python
import os

import plaid
from plaid.api import plaid_api


def get_plaid_client() -> plaid_api.PlaidApi:
    env_name = os.getenv("PLAID_ENV", "sandbox").lower()
    hosts = {
        "sandbox": plaid.Environment.Sandbox,
        "development": plaid.Environment.Development,
        "production": plaid.Environment.Production,
    }
    if env_name not in hosts:
        raise ValueError("PLAID_ENV must be sandbox, development, or production")

    configuration = plaid.Configuration(
        host=hosts[env_name],
        api_key={
            "clientId": os.environ["PLAID_CLIENT_ID"],
            "secret": os.environ["PLAID_SECRET"],
        },
    )
    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)
```

## Calling Endpoints

Import the exact request and enum classes required by the endpoint. Do not pass raw dicts when the generated models exist.

When implementing a product-specific endpoint, first check `references/data-and-openapi.md`, then search `data/api_def.yml` for the endpoint path, `operationId`, and request schema.

Example Link token creation:

```python
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products


def create_link_token(user_id: str) -> str:
    client = get_plaid_client()
    request = LinkTokenCreateRequest(
        products=[Products("transactions")],
        client_name="Cognee Wiki",
        country_codes=[CountryCode("US")],
        language="en",
        user=LinkTokenCreateRequestUser(client_user_id=user_id),
    )
    response = client.link_token_create(request)
    return response["link_token"]
```

Example public token exchange:

```python
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)


def exchange_public_token(public_token: str) -> str:
    client = get_plaid_client()
    response = client.item_public_token_exchange(
        ItemPublicTokenExchangeRequest(public_token=public_token)
    )
    return response["access_token"]
```

Example transactions sync:

```python
from plaid.model.transactions_sync_request import TransactionsSyncRequest


def sync_transactions(access_token: str, cursor: str | None = None) -> dict:
    client = get_plaid_client()
    request = TransactionsSyncRequest(access_token=access_token, cursor=cursor)
    response = client.transactions_sync(request)
    return response.to_dict()
```

## Serialization

Plaid responses are generated model objects. Convert them before returning JSON from APIs or storing them:

```python
import json


payload = response.to_dict()
json_string = json.dumps(payload, default=str)
```

Use `default=str` because Plaid request and response models can include `date`, `datetime`, and decimal-like values.

## Error Handling

Catch `plaid.ApiException`, parse `body`, and branch on Plaid's structured error fields. Preserve the original error for logging, but do not print secrets or access tokens.

```python
import json

import plaid


try:
    response = client.transactions_sync(request)
except plaid.ApiException as exc:
    body = json.loads(exc.body or "{}")
    error_code = body.get("error_code")
    error_type = body.get("error_type")
    display_message = body.get("display_message") or body.get("error_message")
    raise RuntimeError(f"Plaid {error_type}/{error_code}: {display_message}") from exc
```

Common handling:

- `ITEM_LOGIN_REQUIRED`: send the user through Link update mode.
- `INVALID_ACCESS_TOKEN`: remove or quarantine the stored item token and ask the user to reconnect.
- Rate limit errors: retry with backoff only for idempotent reads.

## Implementation Rules

- Use `plaid-python`, not hand-written HTTP calls, unless the package lacks a required beta endpoint.
- Consult Plaid docs, `data/api_def.yml`, or `plaid-openapi` before guessing model names or field shapes.
- Use bundled sample payloads as local fixtures for tests and normalization code instead of inventing response shapes.
- Use Python `date` or timezone-aware `datetime` objects for date/datetime fields.
- Keep `access_token` server-side. Never send it to a browser or model prompt.
- Use Sandbox credentials and sandbox public tokens for local tests.
- Store Plaid tokens encrypted or in a managed secrets store for production code.
- Treat Plaid data as sensitive financial data; minimize logs and redact account numbers, tokens, balances, and personally identifiable information.
