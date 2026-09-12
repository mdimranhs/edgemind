# Deployment Guide

Deploy EdgeMind API to Render with HuggingFace Inference API.

## Prerequisites

- ✅ [Render account](https://dashboard.render.com) (free)
- ✅ [HuggingFace account](https://huggingface.co) + API token
- ✅ GitHub repository

## Quick Deploy (5 minutes)

### 1. Get HuggingFace Token

1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Create new token with **read** access
3. Copy the token (starts with `hf_...`)

### 2. Deploy to Render

#### Option A: Blueprint (Recommended)

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **New +** → **Blueprint**
4. Connect your repository
5. Render detects `render.yaml` automatically
6. **Important:** Add environment variables:
   - `HF_TOKEN` = `hf_your_token_here`
7. Click **Deploy**

#### Option B: Manual

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **Web Service**
3. Connect your repository
4. Configure:
   ```
   Name: edgemind-api
   Runtime: Docker
   Branch: main
   Plan: Free
   ```
5. Add environment variables:
   ```
   LLM_PROVIDER=hf_api
   HF_TOKEN=hf_your_token_here
   HF_MODEL=Qwen/Qwen2.5-1.5B-Instruct
   DEBUG=False
   WEB_SEARCH_ENABLED=True
   ```
6. Set health check path: `/health`
7. Click **Create Web Service**

### 3. Wait for Build

First build takes **5-8 minutes**. Watch logs in dashboard.

### 4. Test Your API

```bash
# Get your URL from Render dashboard
export API_URL="https://edgemind-api.onrender.com"

# Test ping (lightweight)
curl $API_URL/ping

# Test chat
curl -X POST $API_URL/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

✅ **You're live!**

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LLM_PROVIDER` | ✅ Yes | `local` | Set to `hf_api` for cloud inference |
| `HF_TOKEN` | ✅ Yes | - | HuggingFace API token |
| `HF_MODEL` | No | `Qwen/Qwen2.5-1.5B-Instruct` | Model to use |
| `DEBUG` | No | `False` | Enable debug logging |
| `WEB_SEARCH_ENABLED` | No | `True` | Enable web search features |
| `PORT` | No | `8000` | Auto-set by Render |

### Render Settings

**render.yaml** (already in your repo):
```yaml
services:
  - type: web
    name: edgemind-api
    runtime: docker
    plan: free
    branch: main
    healthCheckPath: /health
```

### Docker Configuration

**Dockerfile** (already in your repo):
```dockerfile
FROM python:3.14-slim
WORKDIR /app
# ... optimized for Render
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

---

## Free Tier Limits

| Resource | Limit | EdgeMind Usage |
|----------|-------|----------------|
| RAM | 512MB | ✅ ~200MB (with hf_api) |
| CPU | Shared | ✅ Sufficient |
| Bandwidth | 100GB/month | ✅ Plenty |
| Build time | Unlimited | 5-8 min |
| **Sleep** | After 15 min | ⚠️ See cold starts |

### Cold Start Handling

**Problem:** Free tier sleeps after 15 minutes → 30-60s wake up on first request.

**Solutions:** See [Cold Start Solutions](./cold-start-solutions.md) for complete guide.

**Quick fix:**
1. Set up [UptimeRobot](https://uptimerobot.com) to ping `/ping` every 14 minutes
2. Or run `keepalive.py` on your local machine

---

## Custom Domain (Optional)

### Add Domain

1. Go to your service in Render dashboard
2. Click **Settings** → **Custom Domain**
3. Add your domain (e.g., `api.yourdomain.com`)
4. Configure DNS:
   ```
   Type: CNAME
   Name: api
   Value: edgemind-api.onrender.com
   ```

### Update Frontend

```bash
# .env.local in your Next.js project
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

---

## Monitoring

### Built-in Logs

Render dashboard → Your service → **Logs**

Watch for:
- ✅ `Application startup complete`
- ✅ `Uvicorn running on 0.0.0.0:8000`
- ⚠️ `Cold start detected` (if you added middleware)

### Health Checks

Render automatically pings `/health` every few minutes.

**Response:**
```json
{
  "status": "healthy",
  "service": "EdgeMind API"
}
```

### Add Custom Monitoring

**Option 1: Sentry (Free)**
```bash
pip install sentry-sdk
```

```python
# backend/app/main.py
import sentry_sdk
sentry_sdk.init(dsn="your_sentry_dsn")
```

**Option 2: Logtail (Free)**
```bash
pip install logtail-python
```

---

## Troubleshooting

### Build Fails

**Error:** "Out of memory during pip install"

**Fix:** Already handled in Dockerfile with `--only-binary :all:` flag. If still fails:
```dockerfile
# In Dockerfile, split installs:
RUN pip install fastapi uvicorn pydantic
RUN pip install torch transformers --no-cache-dir
```

### API Not Responding

**Symptom:** Timeout after 10s

**Causes:**
1. **Cold start** (expected on free tier) - Add retry logic in frontend
2. **Health check failing** - Check logs for errors
3. **Environment variable missing** - Verify `HF_TOKEN` is set

**Fix:**
```bash
# Check logs
render logs --tail 100

# Restart service
render services restart edgemind-api
```

### Model Not Available

**Error:** "Model not accessible"

**Causes:**
1. HuggingFace API doesn't support the model
2. Token doesn't have access
3. Model requires agreement to terms

**Fix:**
Try alternative models:
```bash
HF_MODEL=microsoft/Phi-3.5-mini-instruct
# or
HF_MODEL=meta-llama/Llama-3.2-1B-Instruct
```

### High Latency

**Expected latencies:**
- Cold start: 30-60s (first request after sleep)
- Warm start: <1s (API ready)
- Inference: 2-5s (first token from HF API)
- Streaming: <200ms (subsequent tokens)

**Improvements:**
1. Use streaming for better perceived performance
2. Implement retry logic (see [cold-start-solutions.md](./cold-start-solutions.md))
3. Add keepalive to prevent sleep
4. Upgrade to Render Starter ($7/mo) for no sleep

---

## Scaling

### When to Upgrade

**Render Starter ($7/month):**
- ✅ No sleep (zero cold starts)
- ✅ 512MB RAM persistent
- ✅ Better support
- ✅ Custom domain

**Upgrade if:**
- >100 requests/day
- Professional/commercial use
- Portfolio with real traffic
- Cold starts unacceptable

### Horizontal Scaling

Render free tier = 1 instance. For scaling:

**Option 1: Render Starter + multiple instances**
```yaml
# render.yaml
services:
  - type: web
    plan: starter
    numInstances: 3  # Load balanced
```

**Option 2: Add Redis cache**
```yaml
services:
  - type: web
    name: edgemind-api
  
  - type: redis
    name: edgemind-cache
    plan: starter
```

**Option 3: CDN + Edge caching**
- Cloudflare Workers (free tier)
- Vercel Edge Functions (free tier)

See [cold-start-solutions.md](./cold-start-solutions.md) for advanced architectures.

---

## Alternative Platforms

| Platform | Free Tier | Cold Starts | Best For |
|----------|-----------|-------------|----------|
| **Render** | ✅ Yes | ✅ Yes (15min) | Recommended ✅ |
| Railway | ❌ No ($5 trial) | ❌ No | Better performance |
| Fly.io | ✅ Yes (256MB) | ✅ Yes | Global edge |
| Heroku | ❌ Paid only | ❌ No | Legacy apps |
| Vercel | ✅ Yes | ❌ No | Serverless only |

**Why Render:**
- True free tier (no credit card)
- Docker support
- Simple deployment
- Good documentation
- Acceptable cold starts with mitigation

---

## Security Best Practices

### ✅ Do

- Store `HF_TOKEN` in Render environment variables (not in code)
- Use `.env` files locally (gitignored)
- Enable HTTPS (automatic on Render)
- Add rate limiting if public API
- Monitor for abuse in logs

### ❌ Don't

- Commit `.env` files to Git
- Expose API URL without protection
- Use same token for dev/prod
- Skip error handling
- Ignore failed requests in logs

---

## CI/CD

### Auto-deploy on Git Push

Render automatically deploys when you push to `main`:

```bash
git add .
git commit -m "Update feature"
git push origin main

# Render auto-deploys in ~3-5 minutes
```

### Branch Deployments

Deploy different branches:

```yaml
# render.yaml
services:
  - type: web
    name: edgemind-api-staging
    branch: develop  # Staging from develop branch
```

---

## Backup & Migration

### Export Data

SQLite database (if using):
```bash
# Download from Render dashboard
# Settings → Disk → Download
```

### Migrate to Another Platform

1. Export environment variables from Render
2. Update `Dockerfile` if needed
3. Deploy to new platform
4. Update DNS/frontend URL

---

## Cost Projection

### Current (FREE)
```
Render Free Tier:    $0/month
HF Inference API:    $0/month (rate-limited)
─────────────────────────────
Total:               $0/month ✅
```

### Production Scale
```
Render Starter:        $7/month
HF Pro:                $9/month (optional)
PostgreSQL (Neon):     $0-19/month
Redis (Upstash):       $0/month (free tier)
Monitoring (Sentry):   $0/month (free tier)
─────────────────────────────
Total:                 $7-35/month
```

---

## Next Steps

- [ ] Deploy to Render
- [ ] Test all endpoints
- [ ] Set up keepalive (UptimeRobot or `keepalive.py`)
- [ ] Integrate with frontend ([vercel-nextjs.md](./integration/vercel-nextjs.md))
- [ ] Add monitoring (optional)
- [ ] Configure custom domain (optional)

## Resources

- [Render Documentation](https://render.com/docs)
- [HuggingFace Inference API](https://huggingface.co/docs/api-inference)
- [Cold Start Solutions](./cold-start-solutions.md)
- [Integration Guide](./integration/README.md)
