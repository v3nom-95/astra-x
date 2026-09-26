<div align="center">
  <img src="./docs/astra_x_banner.png" alt="ASTRA-X Banner" width="100%" />

  <h1>🛡️ ASTRA-X</h1>
  
  <p><strong>Autonomous Defence Readiness Intelligence Platform</strong></p>

  <p>
    <img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License" />
    <img src="https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/Node.js-18+-339933.svg?logo=node.js&logoColor=white" alt="Node" />
    <img src="https://img.shields.io/badge/Next.js-15-000000.svg?logo=next.js&logoColor=white" alt="Next.js" />
    <img src="https://img.shields.io/badge/FastAPI-009688.svg?logo=fastapi&logoColor=white" alt="FastAPI" />
  </p>
</div>

---

> ⚠️ **IMPORTANT**: This platform focuses **exclusively** on logistics readiness and asset governance. No weapon systems, targeting, surveillance, or combat tooling is implemented.

ASTRA-X is a multi-agent ML-driven logistics readiness and asset governance platform. It demonstrates state-of-the-art ML prediction, agent orchestration, decentralized identity verification (Terminal3 authorization), protected automated actions, comprehensive auditability, and beautiful dashboard visualizations.

---

## 🏗️ Architecture

```mermaid
graph LR
    A[CSV Dataset] -->|Data Processing| B(ML Layer)
    B --> C{Agent Layer}
    C -->|Terminal3 Auth| D[Protected Action]
    C --> E[Audit Log]
    D --> F((Dashboard))
    E --> F
```

### 🧠 ML Models
| Model | Algorithm | Inputs | Output |
|-------|-----------|--------|--------|
| **Inventory Forecast** | LightGBM | `inventory`, `usage_rate` | `days_remaining` |
| **Predictive Maintenance** | XGBoost | `temperature`, `service_days`, `repairs` | `failure_probability` |
| **Risk Detection** | Isolation Forest | `usage_rate`, `service_days`, `repairs` | `risk level (HIGH/MEDIUM/LOW)` |

### 🤖 Agent Pipeline (LangGraph)
```mermaid
sequenceDiagram
    participant Predict as Prediction Layer
    participant Inv as Inventory Agent
    participant Maint as Maintenance Agent
    participant Risk as Risk Agent
    participant Cmd as Command Agent
    participant T3 as Terminal3 Auth
    participant Audit as Audit Agent

    Predict->>Inv: Telemetry & Inventory Data
    Predict->>Maint: Telemetry & Failure Prob
    Predict->>Risk: Anomaly Score
    Inv->>Cmd: Restock Recommendation
    Maint->>Cmd: Repair Recommendation
    Risk->>Cmd: Security/Risk Status
    Cmd->>T3: Request Action Authorization
    T3-->>Cmd: Authorization Token / Denial
    Cmd->>Audit: Log Decision
```

---

## 💻 Tech Stack

- **Frontend**: Next.js 15, TypeScript, Tailwind CSS, shadcn/ui, React Query, Zustand
- **Backend**: FastAPI, SQLAlchemy, Pandas, LangGraph
- **ML**: LightGBM, XGBoost, scikit-learn
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Deployment**: Render (free tier)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm

### ⚙️ Backend Setup
```bash
cd apps/backend
pip install -r requirements.txt
# Copy env file
cp ../../infra/.env.example .env
# Seed database
python seed.py
# Start server
uvicorn main:app --reload --port 8000
```

### 🖥️ Frontend Setup
```bash
cd apps/frontend
npm install
# Set API URL
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

### 🎯 Demo Flow
1. Open [http://localhost:3000](http://localhost:3000)
2. Navigate to **Upload**
3. Upload `data/assets.csv`
4. Click **Run Agent Pipeline**
5. View results on **Dashboard**, **Agents**, **Readiness**, and **Audit** pages

*Expected result for `TRUCK002`:*
- Failure Probability: **91%**
- Action: **schedule_service**
- Authorized: **TRUE**

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/` | API info |
| `POST` | `/upload` | CSV upload + validation |
| `POST` | `/predict` | Batch predictions |
| `POST` | `/predict/inventory` | Inventory forecast |
| `POST` | `/predict/maintenance` | Maintenance prediction |
| `POST` | `/predict/risk` | Risk detection |
| `POST` | `/agent/run` | Run full agent pipeline |
| `POST` | `/authorize` | Terminal3 authorization |
| `GET` | `/dashboard` | Aggregated dashboard data |
| `GET` | `/audit` | Audit log feed |
| `GET` | `/assets` | Asset listing |

Interactive docs available at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📂 Project Structure

```text
astra-x/
├── apps/
│   ├── frontend/              # Next.js 15 App Router
│   │   └── src/
│   │       ├── app/           # Pages (dashboard, upload, assets, agents, readiness, audit)
│   │       ├── components/    # UI components (shadcn + custom)
│   │       ├── lib/           # API client, Zustand store, React Query hooks
│   │       └── types/         # TypeScript definitions
│   └── backend/               # FastAPI monolith
│       ├── api/               # Route handlers
│       ├── models/            # SQLAlchemy ORM
│       ├── schemas/           # Pydantic schemas
│       ├── services/
│       │   ├── ml/            # LightGBM, XGBoost, Isolation Forest
│       │   ├── agents/        # LangGraph workflow + 5 agents
│       │   └── authorization/ # Terminal3 mock adapter
│       ├── db/                # Database engine
│       └── utils/             # Data processing
├── data/                      # Seed CSV dataset
├── infra/                     # render.yaml, .env.example
└── docs/                      # Documentation
```

---

## ☁️ Deployment (Render)

1. Push to GitHub
2. Create a new **Blueprint** on Render
3. Point to `infra/render.yaml`
4. Render provisions: Backend (web service), Frontend (static site), PostgreSQL

See `docs/deployment-guide.md` for details.

---

## 📜 License

This project is licensed under the **Apache License 2.0**. See the [LICENSE](./LICENSE) file for details.
