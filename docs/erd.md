# ASTRA-X Entity Relationship Diagram

## Database Schema

```
┌─────────────────────┐
│       users          │
├─────────────────────┤
│ id          PK INT   │
│ username    UQ STR   │
│ email       UQ STR   │
│ role           STR   │
│ is_active      BOOL  │
│ created_at     DT    │
└─────────────────────┘

┌─────────────────────┐
│       assets         │
├─────────────────────┤
│ id          PK INT   │
│ asset_id    UQ STR   │◄─── Referenced by predictions,
│ type           STR   │     agent_actions, auth_logs,
│ inventory      INT   │     audit_logs via asset_id
│ usage_rate     FLOAT │
│ service_days   INT   │
│ temperature    FLOAT │
│ repairs        INT   │
│ location       STR   │
│ status         STR   │
│ created_at     DT    │
│ updated_at     DT    │
└─────────────────────┘

┌─────────────────────┐
│    predictions       │
├─────────────────────┤
│ id          PK INT   │
│ asset_id    IX STR   │──► assets.asset_id
│ prediction_type STR  │    (inventory/maintenance/risk)
│ input_data     TEXT  │    (JSON)
│ result         TEXT  │    (JSON)
│ confidence     FLOAT │
│ created_at     DT    │
│ batch_id    IX STR   │
└─────────────────────┘

┌─────────────────────┐
│   agent_actions      │
├─────────────────────┤
│ id          PK INT   │
│ agent_name     STR   │
│ asset_id    IX STR   │──► assets.asset_id
│ action         STR   │
│ reason         TEXT  │
│ input_preds    TEXT  │    (JSON)
│ status         STR   │    (pending/authorized/executed)
│ created_at     DT    │
│ batch_id    IX STR   │
└─────────────────────┘

┌──────────────────────┐
│  authorization_logs   │
├──────────────────────┤
│ id          PK INT    │
│ agent_name     STR    │
│ action         STR    │
│ asset_id    IX STR    │──► assets.asset_id
│ authorized     BOOL   │
│ policy_applied STR    │
│ reason         TEXT   │
│ delegated_by   STR   │
│ execution_id   STR   │
│ created_at     DT    │
│ batch_id    IX STR    │
└──────────────────────┘

┌─────────────────────┐
│    audit_logs        │
├─────────────────────┤
│ id          PK INT   │
│ agent_name     STR   │
│ action         STR   │
│ asset_id    IX STR   │──► assets.asset_id
│ authorized     BOOL  │
│ reason         TEXT  │
│ details        TEXT  │    (JSON)
│ severity       STR   │    (INFO/WARNING/CRITICAL)
│ created_at     DT    │
│ batch_id    IX STR   │
└─────────────────────┘
```

## Key Relationships

- All operational tables reference `asset_id` (string) linking back to `assets.asset_id`
- `batch_id` groups related records from a single pipeline run
- JSON columns (`input_data`, `result`, `details`, `input_predictions`) store flexible structured data
- `severity` levels: INFO (normal), WARNING (needs attention), CRITICAL (immediate action)

## Indexes

- `assets.asset_id` — UNIQUE, used for lookups
- `predictions.asset_id` — frequent filtering
- `predictions.batch_id` — batch queries
- `agent_actions.asset_id` — asset-specific queries
- `authorization_logs.asset_id` — authorization lookups
- `audit_logs.asset_id` — audit trail queries
