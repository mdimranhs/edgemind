# Railway Deployment Guide (CLI)

EdgeMind is configured for Railway using [Infrastructure as Code](https://docs.railway.com/infrastructure-as-code) (`.railway/railway.ts`). The Dockerfile builds a CPU-only image and the app talks to Hugging Face Inference API for generation, so it runs on Railway's free/paid plans without a GPU.

## Prerequisites

- Railway CLI **>= 5.42.1** (the IaC engine ships in the CLI). Install or upgrade:
  ```bash
  bash <(curl -fsSL railway.com/install.sh) -y
  railway --version
  ```
- Docker (only needed for `railway up` from local code).
- A Hugging Face access token (`HF_TOKEN`).

## One-time setup

Install the TypeScript SDK so the CLI can evaluate `.railway/railway.ts`:

```bash
npm install
```

## Deploy to a new project

```bash
# 1. Authenticate (new account, browserless works too: `railway login --browserless`)
railway login

# 2. Create a project for this repo and link it (name it, e.g. "edgemind")
railway init

# 3. Preview what IaC will create — the "edgemind" service, /health check, and env vars
railway config plan

# 4. Apply it (creates the service and non-secret environment variables)
railway config apply

# 5. Set the secret on Railway — it is preserved (`preserve()`) in IaC, so it is
#    never written to code and is never overwritten by a re-apply
railway variables set "HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx"
railway variables | grep HF_TOKEN   # confirm

# 6. Deploy the Docker image from local code
railway up

# 7. Generate a public URL
railway domain
```

URLs and the healthcheck: after `railway domain`, `curl https://<your-app>.up.railway.app/health` should return `{"status":"healthy","service":"EdgeMind API"}`.

## Redeploying

```bash
railway up            # upload and deploy the current directory
railway up --ci       # build logs only, exits when the build completes
railway redeploy      # restart the same image
```

## Environment variables

Non-secret variables are owned by `.railway/railway.ts` (`env` block). `HF_TOKEN` uses `preserve()`, meaning Railway keeps whatever value is set there — set it via the dashboard or `railway variables set`.

| Variable | Default | Notes |
|----------|---------|-------|
| `LLM_PROVIDER` | `hf_api` | Cloud inference via Hugging Face Inference API |
| `HF_MODEL` | `Qwen/Qwen3-8B` | Any model your Hugging Face providers support |
| `HF_TOKEN` | *(on Railway)* | Set with `railway variables set`, never committed |
| `DEBUG` | `false` | |
| `WEB_SEARCH_ENABLED` | `true` | Web-search fallback |
| `RAG_LOCAL_FILES_ONLY` | `true` | Keep RAG grounded in the bundled knowledge base |

Change a non-secret variable in `railway.ts`, then `railway config plan` → `railway config apply`.

## Notes & limits

- **Port:** Railway injects a dynamic `$PORT`; the Dockerfile CMD is `uvicorn ... --port ${PORT:-8000}` so it binds whatever Railway provides.
- **Persistence:** SQLite history and the prebuilt FAISS index live inside the container. Railway's filesystem is ephemeral — conversation memory resets on every redeploy. To persist it, attach a Volume mounted at `/app/app` (where `chat_history.db` is written). This is a future migration; the API stays fully functional without it.
- **Model downloads:** the embedder (`all-MiniLM-L6-v2`) is baked into the image at build time (`HF_HOME=/opt/huggingface`), so instances never download it at request time.