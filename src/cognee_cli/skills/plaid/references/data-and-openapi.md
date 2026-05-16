# Plaid Bundled Reference Data

Use these local files before guessing Plaid request or response shapes:

- `data/api_def.yml`: full Plaid OpenAPI 3.0 spec. Search this file for endpoint paths, `operationId`, request schemas, response schemas, enum values, required fields, and pagination notes.
- `data/Auth.json`: sample `/auth/get` response with accounts, item metadata, and ACH numbers.
- `data/Balance.json`: sample `/accounts/balance/get` response with depository, credit, and student loan-style balances.
- `data/Identity.json`: sample `/identity/get` response with account data plus names, addresses, emails, and phone numbers.
- `data/Transactions.json`: sample `/transactions/get` style response with accounts, item metadata, `total_transactions`, and transaction objects.
- `data/Assets_Report.json`: sample `/asset_report/get` response with report metadata, items, accounts, historical balances, owners, transactions, and warnings.

## OpenAPI Lookup

Prefer targeted `rg` searches over loading the full OpenAPI file into context:

```bash
rg -n "/transactions/sync|operationId: transactionsSync|TransactionsSyncRequest" src/cognee_cli/skills/plaid/data/api_def.yml
rg -n "components/schemas/(AuthGetRequest|AuthGetResponse)" src/cognee_cli/skills/plaid/data/api_def.yml
rg -n "enum:|Products|CountryCode" src/cognee_cli/skills/plaid/data/api_def.yml
```

Common endpoint to Python client mappings:

| API path | `PlaidApi` method | Request model |
| --- | --- | --- |
| `/link/token/create` | `link_token_create` | `LinkTokenCreateRequest` |
| `/item/public_token/exchange` | `item_public_token_exchange` | `ItemPublicTokenExchangeRequest` |
| `/auth/get` | `auth_get` | `AuthGetRequest` |
| `/accounts/balance/get` | `accounts_balance_get` | `AccountsBalanceGetRequest` |
| `/identity/get` | `identity_get` | `IdentityGetRequest` |
| `/transactions/get` | `transactions_get` | `TransactionsGetRequest` |
| `/transactions/sync` | `transactions_sync` | `TransactionsSyncRequest` |
| `/asset_report/create` | `asset_report_create` | `AssetReportCreateRequest` |
| `/asset_report/get` | `asset_report_get` | `AssetReportGetRequest` |

## Sample Payload Usage

Use sample data for tests, fixtures, response normalization, and schema exploration. Keep these payloads local-only; they are examples, not live Plaid data.

Key response fields by product:

- Auth: `accounts`, `numbers`, `item`, `request_id`.
- Balance: `accounts[].balances.available`, `current`, `limit`, `iso_currency_code` when present.
- Identity: `identity.names`, `identity.addresses`, `identity.emails`, `identity.phone_numbers`.
- Transactions: `accounts`, `transactions`, `total_transactions`, `item`, `request_id`.
- Asset Reports: `report.asset_report_id`, `report.items[].accounts[]`, `historical_balances`, `transactions`, `warnings`.

When building tests, load JSON with `json.load()` from the skill directory rather than embedding large payloads in test files.

## Transactions Pagination

For `/transactions/sync`, always persist `next_cursor`. If pagination fails after a page with `has_more=true`, restart the pagination loop from the cursor used on the first page of that update, not only the failed page. Plaid documents this behavior in `api_def.yml` near the `transactionsSync` operation.

## Safety

Never treat bundled sample identifiers as real credentials. Continue to redact access tokens, account numbers, balances, names, addresses, phone numbers, emails, and Plaid item IDs in logs and model prompts.
