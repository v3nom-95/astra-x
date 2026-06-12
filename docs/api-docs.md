# ASTRA-X API Documentation

Base URL: `http://localhost:8000` (dev) or `https://astra-x-api.onrender.com` (prod)

Interactive docs: `/docs` (Swagger) or `/redoc` (ReDoc)

---

## Health

### GET /health
Returns system health status.

**Response:**
```json
{
  "status": "healthy",
  "environment": "development",
  "database": "connected",
  "ml_models": {
    "inventory": "ready",
    "maintenance": "ready",
    "risk": "ready"
  },
  "version": "1.0.0"
}
```

---

## Upload

### POST /upload
Upload CSV dataset to train models and load assets.

**Content-Type:** `multipart/form-data`

**Body:** `file` — CSV file with columns: `asset_id, type, inventory, usage_rate, service_days, temperature, repairs, location, status`

**Response:**
```json
{
  "message": "Successfully loaded 35 assets",
  "assets_loaded": 35,
  "batch_id": "a1b2c3d4",
  "validation_errors": []
}
```

---

## Predictions

### POST /predict
Run all predictions for assets in database.

**Body (optional):**
```json
["TRUCK001", "TRUCK002"]
```

**Response:**
```json
{
  "batch_id": "e5f6g7h8",
  "predictions": [
    {
      "asset_id": "TRUCK002",
      "inventory": { "asset_id": "TRUCK002", "days_remaining": 10.5, "needs_restock": true },
      "maintenance": { "asset_id": "TRUCK002", "failure_probability": 0.91, "needs_service": true },
      "risk": { "asset_id": "TRUCK002", "risk": "HIGH", "anomaly_score": 0.65 }
    }
  ],
  "total_assets": 1,
  "high_risk_count": 1,
  "needs_service_count": 1,
  "needs_restock_count": 1
}
```

### POST /predict/inventory
Single asset inventory forecast.

### POST /predict/maintenance
Single asset maintenance prediction.

### POST /predict/risk
Single asset risk detection.

---

## Agents

### POST /agent/run
Execute the full LangGraph agent pipeline.

**Body:**
```json
{
  "asset_ids": null,
  "batch_id": null
}
```

**Response:**
```json
{
  "batch_id": "i9j0k1l2",
  "decisions": [
    {
      "agent_name": "command_agent",
      "asset_id": "TRUCK002",
      "action": "schedule_service",
      "reason": "Command decision: schedule_service | Coordinated from: schedule_service, approve_restock, freeze_operation",
      "confidence": 0.95
    }
  ],
  "authorizations": [...],
  "audit_entries": [...],
  "summary": {
    "total_assets": 35,
    "high_risk_count": 7,
    "needs_service_count": 12,
    "needs_restock_count": 8,
    "total_actions": 35,
    "authorized_count": 35,
    "rejected_count": 0
  }
}
```

---

## Authorization

### POST /authorize
Authorize a single action through Terminal3.

**Body:**
```json
{
  "agent_name": "maintenance_agent",
  "action": "schedule_service",
  "asset_id": "TRUCK002",
  "reason": "High failure probability"
}
```

**Response:**
```json
{
  "authorized": true,
  "policy_applied": "maintenance_operations",
  "execution_id": "uuid-here",
  "reason": "Auto-approved by policy"
}
```

---

## Dashboard

### GET /dashboard
Aggregated readiness data.

---

## Audit

### GET /audit
Paginated audit logs.

**Query Params:** `page`, `page_size`, `asset_id`, `agent_name`, `severity`

---

## Assets

### GET /assets
List all assets.

**Query Params:** `status`, `asset_type`, `location`
