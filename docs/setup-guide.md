# ASTRA-X Setup Guide

## Local Development Setup

### System Requirements

- **Python**: 3.11+ (3.11 recommended)
- **Node.js**: 18+ (20 LTS recommended)
- **npm**: 9+
- **Git**: Latest

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USER/astra-x.git
cd astra-x
```

### Step 2: Backend Setup

```bash
cd apps/backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../../infra/.env.example .env
# Edit .env if needed (defaults work for local dev)

# Seed the database
python seed.py

# Start the server
uvicorn main:app --reload --port 8000
```

The backend will:
1. Create SQLite database (`astra_x.db`)
2. Train ML models from seed CSV
3. Cache models to `./model_cache/`
4. Start on http://localhost:8000

Verify: http://localhost:8000/health

### Step 3: Frontend Setup

```bash
cd apps/frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start dev server
npm run dev
```

Frontend starts on http://localhost:3000

### Step 4: Run the Demo

1. Open http://localhost:3000
2. Go to **Upload** page
3. Upload `data/assets.csv` (included in repo)
4. Click **Upload & Train Models**
5. Click **Run Agent Pipeline**
6. Navigate to **Dashboard** to see results
7. Check **Audit** for complete decision trail

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./astra_x.db` | Database connection string |
| `ENVIRONMENT` | `development` | Environment name |
| `MODEL_CACHE_DIR` | `./model_cache` | ML model cache directory |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed CORS origins |
| `OPENAI_API_KEY` | (placeholder) | Future use — not required |
| `TERMINAL3_API_KEY` | (placeholder) | Future use — not required |

### Using PostgreSQL Locally

```bash
# Update .env
DATABASE_URL=postgresql://user:pass@localhost:5432/astra_x

# Create database
createdb astra_x

# Seed
python seed.py
```
