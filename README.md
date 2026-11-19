---
title: EdgeMind
emoji: 🧠
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
---

# EdgeMind 🧠

Standalone AI assistant API powered by FastAPI and Hugging Face. Run it locally or deploy it as a container to Hugging Face Spaces or Railway. Chat is stateless by default; SQLite history is opt-in.


## ✨ Features

- **🚀 Deployment ready** — Docker image for Railway (IaC) and Amazon ECR / ECS Express Mode
- **🔄 Streaming** — Token-by-token via Server-Sent Events
- **🧠 RAG** — FAISS + Sentence Transformers, MMR diversification, source attribution
- **🧠 Conversation context** — Clients send recent turns; server storage is off by default, with optional local SQLite history
- **🔌 Model providers** — Local Hugging Face Transformers, Hugging Face Inference API, or a mock provider for development
- **⚡ Production optimizations** — Lazy initialization, background warmup, graceful cold starts

## 🏗️ Tech Stack

- **Backend:** Python 3.14 / FastAPI / Uvicorn
- **AI:** HuggingFace Transformers / PyTorch / Sentence Transformers
- **Search:** FAISS (vector similarity)
- **Optional history:** SQLite (aiosqlite), disabled by default
- **Deployment:** Docker / Railway (CLI + IaC) / Amazon ECR / ECS Express Mode / Vercel-ready

## 🚀 Quick Start

### Local Development

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
python -m pip install --index-url https://download.pytorch.org/whl/cpu "torch==2.12.1+cpu"
python -m pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

The first local start downloads the embedding model if it is not cached. Set `RAG_LOCAL_FILES_ONLY=true` only when the model is already available locally.

### Test API

```bash
# Health check
curl http://localhost:8000/health

# Non-streaming chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role":"user", "content":"Hello!"}]}'

# Streaming chat
curl -N -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role":"user", "content":"Explain RAG"}], "stream": true}'
```

## 📚 Documentation

### Getting Started
- **[Railway Deployment Guide](docs/railway.md)** - Deploy with the Railway CLI + IaC
- **[Deployment Guide](docs/deployment.md)** - Deploy to AWS ECR and ECS Express Mode
- **[API Reference](docs/api.md)** - Complete endpoint documentation
- **[Architecture](docs/architecture.md)** - System design and components

### Integration
- **[Integration Guide](docs/integration/README.md)** - Connect your frontend
- **[Vercel + Next.js](docs/integration/vercel-nextjs.md)** - Full Next.js integration
- **[React Component](docs/integration/react-example.jsx)** - Drop-in chat widget
- **[JavaScript Client](docs/integration/client-example.js)** - Production client

### Production
- **[Architecture](docs/architecture.md)** - AWS target architecture and migration path
- **[Roadmap](docs/roadmap.md)** - Future features

## 🎯 Use Cases

### Portfolio Integration
Power your portfolio with an AI assistant. Example: [mdimranhs.vercel.app](https://mdimranhs.vercel.app)

```javascript
// Next.js integration
import { EdgeMindChat } from './EdgeMindChat';

<EdgeMindChat 
  apiUrl="/api/chat"
  systemPrompt="Help visitors learn about Md Imran Hossain's work"
/>
```

See: [Vercel Integration Guide](docs/integration/vercel-nextjs.md)

### Standalone API
Deploy as a standalone service for any frontend:

```bash
# Deploy to Railway
railway up

# Or deploy to AWS
docker build --platform linux/amd64 -t edgemind-api .

# Use from anywhere
curl https://your-endpoint/chat -d '...'
```

See: [Railway Deployment Guide](docs/railway.md) · [Deployment Guide](docs/deployment.md)

## 📊 Progress

| Feature | Status |
|---------|--------|
| Base LLM integration | ✅ Complete |
| Streaming responses | ✅ Complete |
| RAG with FAISS | ✅ Complete |
| MMR + source attribution | ✅ Complete |
| Conversation memory | ✅ Complete |
| Production optimizations | ✅ Complete |
| AWS container deployment | 🚧 In progress |
| Railway deployment (CLI + IaC) | ✅ Complete |
| Cloud database and vector store | 🚧 Planned |
| Frontend integration docs | ✅ Complete |
| Fine-tuned model | ⏸️ On hold |

## 🛠️ Configuration

### Environment Variables

```bash
# backend/.env
LLM_PROVIDER=hf_api              # local | hf_api | mock
HF_TOKEN=hf_your_token_here      # HuggingFace API token
HF_MODEL=Qwen/Qwen3-8B
DEBUG=False
WEB_SEARCH_ENABLED=True
```

### Providers

- **`hf_api`** - HuggingFace Inference API (recommended for deployment)
- **`local`** - Local model on GPU (development only)
- **`mock`** - deterministic development provider; no model download or API key required

## 🌐 Deployment

### Railway (CLI)

Deployment is defined in code with [Infrastructure as Code](docs/railway.md) — `.railway/railway.ts` creates the `edgemind` service, `/health` check, and environment variables.

```bash
npm install              # Railway IaC SDK
railway login
railway init             # create a project
railway config apply     # apply infra (service + env)
railway variables set "HF_TOKEN=hf_..."   # secret stays out of git
railway up               # build & deploy the Docker image
railway domain           # generate a public URL
```

See: [Railway Deployment Guide](docs/railway.md)

### AWS ECS Express Mode

```bash
# Build and push to ECR, then deploy the image through ECS Express Mode.
# See docs/deployment.md for the complete AWS CLI workflow.
```

ECS Express Mode provides a managed Fargate service, HTTPS endpoint, load balancing, scaling, and CloudWatch monitoring. See: [Deployment Guide](docs/deployment.md)

## 🤝 Contributing

Contributions welcome! See [Roadmap](docs/roadmap.md) for planned features.

## 📄 License

MIT License - see LICENSE file

## 🔗 Links

- **Live API:** Configure after deploying on Railway (`railway domain`) or AWS ECS
- **Portfolio:** [mdimranhs.vercel.app](https://mdimranhs.vercel.app)
- **Documentation:** [docs/](docs/)

---

Built with ❤️ by [Md Imran Hossain](https://mdimranhs.vercel.app)
