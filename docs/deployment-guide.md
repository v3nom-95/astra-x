# ASTRA-X Render Deployment Guide
### Comprehensive Production Setup & Orchestration Manual

This document provides a step-by-step, zero-to-production guide for deploying the complete ASTRA-X platform on Render. It outlines the architecture components, required environment variables, build/start commands, manual vs. blueprint deployment options, and troubleshooting steps.

---

## 1. Deployment Architecture Overview

On Render, the platform is split into four distinct connected services running on the **Free Tier**:

```
 ┌────────────────────────────────────────────────────────┐
 │                   NEXT.JS FRONTEND                     │
 │          (Static Site - Render Static CDN)             │
 └──────────────────────────┬─────────────────────────────┘
                            │
                            │ (Public API HTTPS Requests)
                            ▼
 ┌────────────────────────────────────────────────────────┐
 │                  FASTAPI BACKEND API                   │
 │           (Python 3.11 - Render Web Service)           │
 └──────────────┬──────────────────────────┬──────────────┘
                │                          │
  (SQLAlchemy)  │                          │ (HTTP API Client)
                ▼                          ▼
 ┌──────────────────────────┐    ┌────────────────────────┐
 │   POSTGRESQL DATABASE    │    │   TERMINAL 3 BRIDGE    │
 │   (Render DB Instance)   │    │  (Node.js Web Service) │
 └──────────────────────────┘    └────────────────────────┘
```

---

## 2. Option A: Automated Deployment (Render Blueprint) - *RECOMMENDED*

ASTRA-X contains a predefined Blueprint file at [infra/render.yaml](file:///c:/Users/venka/.gemini/antigravity-ide/scratch/astra-x/infra/render.yaml). Using this will automatically configure and link all four services together in a single click.

### Step-by-Step Blueprint Walkthrough:
1.  Push your code to a private or public **GitHub** repository.
2.  Go to the [Render Dashboard](https://dashboard.render.com).
3.  Click **New +** (top right) and select **Blueprint**.
4.  Connect your GitHub account and select the `astra-x` repository.
5.  Render will parse [infra/render.yaml](file:///c:/Users/venka/.gemini/antigravity-ide/scratch/astra-x/infra/render.yaml) and present a list of services to deploy.
6.  Fill in the required environment variables (see **Section 4: Environment Variables Registry** below) when prompted.
7.  Click **Apply**.

---

## 3. Option B: Manual Service-by-Service Deployment

If you prefer to configure each service manually in the Render dashboard, follow these configurations:

### 1. PostgreSQL Database (`astra-x-db`)
*   **Service Type:** PostgreSQL Database
*   **Database Name:** `astra_x`
*   **User:** `astra_admin` (or auto-generated)
*   **PostgreSQL Version:** `16`
*   **Plan:** Free

### 2. Terminal 3 Node Bridge (`astra-x-t3-bridge`)
This service runs the local Express server that loads the `@terminal3/t3n-sdk` WASM runtime.
*   **Service Type:** Web Service
*   **Runtime:** `Node`
*   **Root Directory:** `apps/t3-bridge`
*   **Build Command:** `npm install`
*   **Start Command:** `npm start`
*   **Plan:** Free

### 3. FastAPI Backend API (`astra-x-api`)
This runs the Python ML prediction models, SQL database manager, and LangGraph workflow.
*   **Service Type:** Web Service
*   **Runtime:** `Python`
*   **Root Directory:** `apps/backend`
*   **Build Command:** `pip install -r requirements.txt`
*   **Start Command:** `python -c "from main import init_db; init_db()" && uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`
    *(Note: The startup command runs a small Python inline execution to compile the SQL tables inside Postgres before starting the Uvicorn worker.)*
*   **Plan:** Free

### 4. Next.js Frontend (`astra-x-frontend`)
This compiles and exports your React application to static assets.
*   **Service Type:** Static Site (or Web Service set to Static)
*   **Runtime:** `Static`
*   **Root Directory:** `apps/frontend`
*   **Build Command:** `npm install && npm run build`
*   **Publish Directory:** `out`
*   **Plan:** Free

---

## 4. Environment Variables Registry

Ensure these environment variables are populated on the respective services.

### 4.1 Backend Web Service (`astra-x-api`)

| Variable Key | Description | Example / Recommended Value | Source / Notes |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection string. | `postgresql://user:pass@host/db` | Automatically populated if using Blueprint. Otherwise, copy from your Render DB dashboard. |
| `ENVIRONMENT` | Defines app configuration environment. | `production` | Enables strict CORS and security settings when set to `production`. |
| `CORS_ORIGINS` | Permitted frontend origins. | `https://astra-x-frontend.onrender.com` | Restricts API access strictly to your deployed frontend. |
| `TERMINAL3_API_KEY` | Private key to initialize T3 client. | `0x...` | Your Ethereum private key registered with the Terminal 3 Network. |
| `TERMINAL3_BASE_URL` | Target location of T3 Bridge API. | `https://astra-x-t3-bridge.onrender.com/v1` | Points to the route of your deployed T3 Bridge service. |
| `MODEL_CACHE_DIR` | Cache directory for ML models. | `/tmp/model_cache` | Redirects LightGBM/XGBoost serializations to Render's local ephemeral path. |
| `PYTHON_VERSION` | Python binary version. | `3.11.11` | Tells Render which version of Python environment to provision. |

### 4.2 Terminal 3 Bridge (`astra-x-t3-bridge`)

| Variable Key | Description | Example / Recommended Value | Source / Notes |
| :--- | :--- | :--- | :--- |
| `TERMINAL3_API_KEY` | Private key to sign bridge handshakes. | `0x...` | Must match the key used in the backend. Used to establish the agent's DID. |
| `PORT` | Local bridge listening port. | `3001` (Default) | Render automatically injects this for incoming requests. |

### 4.3 Next.js Frontend (`astra-x-frontend`)

| Variable Key | Description | Example / Recommended Value | Source / Notes |
| :--- | :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | Public endpoint of the backend. | `https://astra-x-api.onrender.com` | **CRITICAL:** Next.js compiles this variable into the client bundle at build-time. Must match backend URL. |

---

## 5. Post-Deployment Verification Checklist

Once Render shows all green build statuses:

1.  **Backend Status:** Navigate to `https://your-api-name.onrender.com/health` in your browser. It should return:
    ```json
    {
      "status": "healthy",
      "environment": "production",
      "database": "connected",
      "ml_models": {
        "inventory": "ready",
        "maintenance": "ready",
        "risk": "ready"
      }
    }
    ```
2.  **API Enpoints Docs:** Verify documentation loads at `https://your-api-name.onrender.com/docs`.
3.  **Frontend Interface:** Open `https://your-frontend-name.onrender.com`.
4.  **Ingestion Seeding:**
    *   Navigate to `/upload` on the frontend.
    *   Upload [t3_usecase_demo.csv](file:///c:/Users/venka/.gemini/antigravity-ide/scratch/astra-x/data/t3_usecase_demo.csv). This validates the parser, inserts records into the PostgreSQL database, and trains/caches the ML models on the active server.
5.  **Agent Verification:** Click **Run Agent Pipeline** on the dashboard. Navigate to `/audit` to verify that cryptographic logs generated from the T3 Bridge are successfully written to your PostgreSQL database.

---

## 6. Troubleshooting Common Deployment Faults

### 6.1 Backend Crash: Database Connection Failures
*   **Symptom:** Backend build fails or startup command loops with `Connection refused` or `database system is starting up`.
*   **Resolution:** When first deploying via Blueprint, the PostgreSQL service and FastAPI service start simultaneously. Sometimes, Python tries to query PostgreSQL before it has fully initialized. Simply click **Manual Deploy -> Clear Cache & Deploy** on the backend web service in the Render dashboard to restart the initialization sequence.

### 6.2 Frontend Show "Network Error" or 0 Assets
*   **Symptom:** Dashboard loads but displays no assets or fails to upload files.
*   **Resolution:** 
    1. Open your browser console (F12) and inspect the failed requests.
    2. If it is a CORS error, check that the backend environment variable `CORS_ORIGINS` exactly matches your frontend URL (no trailing slashes).
    3. If it is a `404 Not Found` or `Connection Refused` error, check that `NEXT_PUBLIC_API_URL` is set correctly on the frontend and trigger a rebuild of the static site.

### 6.3 T3 Bridge "WASM loader" Failures
*   **Symptom:** Node.js logs error: `Cannot find module '@terminal3/t3n-sdk'` or WASM initialization throws memory errors.
*   **Resolution:** The Terminal 3 SDK uses native WebAssembly components. Ensure your bridge service on Render is running on **Node.js v18 or v20** (Render uses Node 20 by default, which is compatible). Check that the bridge build command correctly executes `npm install` to download the precompiled WASM binaries.
