# ASTRA-X Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        ASTRA-X Platform                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────────────────────────────┐  │
│  │   Frontend    │    │            Backend (FastAPI)          │  │
│  │   Next.js 15  │◄──►│                                      │  │
│  │              │    │  ┌────────────────────────────────┐   │  │
│  │  • Dashboard  │    │  │         API Layer               │   │  │
│  │  • Upload     │    │  │  /upload /predict /agent/run   │   │  │
│  │  • Assets     │    │  │  /authorize /dashboard /audit  │   │  │
│  │  • Agents     │    │  └──────────┬─────────────────────┘   │  │
│  │  • Readiness  │    │             │                          │  │
│  │  • Audit      │    │  ┌──────────▼─────────────────────┐   │  │
│  └──────────────┘    │  │       ML Layer                   │   │  │
│                       │  │  ┌─────────┐ ┌───────┐ ┌─────┐ │   │  │
│                       │  │  │LightGBM │ │XGBoost│ │IForest│ │   │  │
│                       │  │  │Inventory│ │Maint. │ │Risk  │ │   │  │
│                       │  │  └────┬────┘ └───┬───┘ └──┬───┘ │   │  │
│                       │  └───────┼──────────┼────────┼─────┘   │  │
│                       │          │          │        │          │  │
│                       │  ┌───────▼──────────▼────────▼─────┐   │  │
│                       │  │     Agent Layer (LangGraph)      │   │  │
│                       │  │                                  │   │  │
│                       │  │  Inventory ──► Maintenance ──►   │   │  │
│                       │  │  Risk ──► Command ──► Audit      │   │  │
│                       │  └──────────────┬───────────────────┘   │  │
│                       │                 │                       │  │
│                       │  ┌──────────────▼───────────────────┐   │  │
│                       │  │   Terminal3 Authorization        │   │  │
│                       │  │   • Agent Identity               │   │  │
│                       │  │   • Protected Actions            │   │  │
│                       │  │   • Policy Engine                │   │  │
│                       │  │   • Execution Logs               │   │  │
│                       │  └──────────────┬───────────────────┘   │  │
│                       │                 │                       │  │
│                       │  ┌──────────────▼───────────────────┐   │  │
│                       │  │       Database (PostgreSQL)       │   │  │
│                       │  │  users │ assets │ predictions     │   │  │
│                       │  │  agent_actions │ auth_logs │ audit│   │  │
│                       │  └──────────────────────────────────┘   │  │
│                       └──────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
1. User uploads CSV
       │
       ▼
2. Data Validation & Storage
       │
       ▼
3. ML Model Training (auto on startup / upload)
       │
       ▼
4. Batch Predictions
   ├── Inventory Forecast (LightGBM)
   ├── Maintenance Prediction (XGBoost)
   └── Risk Detection (Isolation Forest)
       │
       ▼
5. Agent Pipeline (LangGraph StateGraph)
   ├── Inventory Agent → approve_restock / delay_restock
   ├── Maintenance Agent → schedule_service / continue_operation
   ├── Risk Agent → freeze_operation / monitor
   ├── Command Agent → coordinate & prioritize
   ├── Terminal3 Authorization → authorize / deny
   └── Audit Agent → generate audit records
       │
       ▼
6. Dashboard Visualization
   ├── Readiness Score
   ├── Prediction Cards
   ├── Agent Timeline
   ├── Authorization Log
   └── Audit Feed
```

## Terminal3 Authorization Flow

```
Agent Request
     │
     ▼
┌─────────────────┐
│ request_action() │ ─── Create ActionRequest
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   authorize()    │ ─── Check policies, permissions, roles
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
 APPROVED  DENIED
    │         │
    ▼         ▼
┌────────┐ ┌────────┐
│execute()│ │  log   │
└───┬────┘ └────────┘
    │
    ▼
┌─────────┐
│ audit() │ ─── Generate audit record
└─────────┘
```
