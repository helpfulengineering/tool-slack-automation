---
problem: migrate onboarding assistant persistence from Airtable to Google Sheets
backends:
  - airtable
  - google sheets
flags:
  DATA_BACKEND:
    description: primary persistence backend
    values: [airtable, sheets]
  WRITE_BACKENDS:
    description: comma-separated list of backends to write to
    values: [airtable, sheets, airtable,sheets]
gaps:
  - does not emulate Airtable RECORD_ID() values
  - does not preserve Airtable formula/lookup/rollup fields
  - does not preserve Airtable auto-number fields
  - does not preserve Airtable linked-record UI semantics
---

# Onboarding Assistant: Airtable → Google Sheets context

## Goal
Migrate the onboarding assistant data layer from Airtable to Google Sheets using a backend adapter and feature flags.

## Current code structure
- `onboarding-assistant/code/modules/database/__init__.py`
  - selects the active backend using `DATA_BACKEND`
  - supports dual writes using `WRITE_BACKENDS`
- `onboarding-assistant/code/modules/database/airtable.py`
  - current Airtable provider
  - handles `Volunteers`, `Email Addresses`, and `Events`/engagement tables
- `onboarding-assistant/code/modules/database/sheets.py`
  - new Google Sheets provider implementation
  - stores `Volunteers`, `Email Addresses`, `Events`, and normalized tag sheets
- `onboarding-assistant/code/modules/analytics/__init__.py`
  - sends analytics events through the same database facade

## Data model and schemas
### Primary records
- `Volunteers`
- `Email Addresses`
- `Events`

### Tag/lookup sheets
- `Skills`
- `Languages`
- `Industries`

### Google Sheets workbook layout
One spreadsheet with tabs:
- `Volunteers`
- `Email Addresses`
- `Events`
- `Skills`
- `Languages`
- `Industries`

## Migration strategy
1. Keep Airtable as the authoritative read source:
   - `DATA_BACKEND=airtable`
   - `WRITE_BACKENDS=airtable,sheets`
2. Seed Sheets with all writes while reads remain on Airtable
3. Validate parity and fix any data mapping issues
4. Cut over reads to Sheets:
   - `DATA_BACKEND=sheets`
5. Optionally keep dual writes while Sheets proves stable
6. Retire Airtable writes once cutover is complete

## Known limitations
- Sheets provider creates its own stable row IDs, not Airtable `RECORD_ID()` values
- Airtable auto-generated and formula-derived fields are not mirrored
- lookup/rollup fields are not automatically reproduced in Sheets
- Google Sheets only emulates relationships via serialized tag IDs and normalized tag tables
- Data model is intentionally denormalized compared to Airtable’s linked records

## Important notes for future agents
- use `DATA_BACKEND` to choose the active backend
- use `WRITE_BACKENDS` to write to both backends during migration
- the Sheets provider requires `google_sheets_spreadsheet_id` and `google_service_account_key`
- `amazon.configuration` loads AWS Secrets Manager values for runtime config

## Files touched
- `onboarding-assistant/code/modules/database/__init__.py`
- `onboarding-assistant/code/modules/database/airtable.py`
- `onboarding-assistant/code/modules/database/sheets.py`
- `onboarding-assistant/code/airtable_schema_discovery.py`
- `onboarding-assistant/code/requirements.txt`
- `onboarding-assistant/code/pyproject.toml`
