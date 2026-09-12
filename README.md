# EdgeMind 🧠

Production-ready AI assistant backend powered by FastAPI and HuggingFace. Deploy on free tier with streaming, RAG, and conversation memory.

## ✨ Features

- **🚀 Deployment ready** — Optimized for Render free tier with cold start mitigation
- **🔄 Streaming** — Token-by-token via Server-Sent Events
- **🧠 RAG** — FAISS + Sentence Transformers, MMR diversification, source attribution
- **💾 Conversation memory** — Per-session history in SQLite
- **🔌 Modular providers** — Local HuggingFace / Cloud Inference API / OpenAI / Ollama
- **⚡ Production optimizations** — Lazy initialization, background warmup, graceful cold starts

## 🏗️ Tech Stack

- **Backend:** Python 3.14 / FastAPI / Uvicorn
- **AI:** HuggingFace Transformers / PyTorch / Sentence Transformers
- **Search:** FAISS (vector similarity)
- **Database:** SQLite (aiosqlite)
- **Deployment:** Docker / Render / Vercel-ready

## 🚀 Quick Start

### Local Development

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Test API

```bash
# Health check
curl http://localhost:8000/ping

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
- **[Deployment Guide](docs/deployment.md)** - Deploy to Render in 5 minutes
- **[API Reference](docs/api.md)** - Complete endpoint documentation
- **[Architecture](docs/architecture.md)** - System design and components

### Integration
- **[Integration Guide](docs/integration/README.md)** - Connect your frontend
- **[Vercel + Next.js](docs/integration/vercel-nextjs.md)** - Full Next.js integration
- **[React Component](docs/integration/react-example.jsx)** - Drop-in chat widget
- **[JavaScript Client](docs/integration/client-example.js)** - Production client

### Production
- **[Cold Start Solutions](docs/cold-start-solutions.md)** - Handle Render free tier sleep
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
# Deploy to Render
git push origin main  # Auto-deploys via render.yaml

# Use from anywhere
curl https://your-api.onrender.com/chat -d '...'
```

See: [Deployment Guide](docs/deployment.md)

## 📊 Progress

| Feature | Status |
|---------|--------|
| Base LLM integration | ✅ Complete |
| Streaming responses | ✅ Complete |
| RAG with FAISS | ✅ Complete |
| MMR + source attribution | ✅ Complete |
| Conversation memory | ✅ Complete |
| Production optimizations | ✅ Complete |
| Render deployment config | ✅ Complete |
| Cold start mitigation | ✅ Complete |
| Frontend integration docs | ✅ Complete |
| Fine-tuned model | ⏸️ On hold |

## 🛠️ Configuration

### Environment Variables

```bash
# backend/.env
LLM_PROVIDER=hf_api              # local | hf_api | openai | ollama
HF_TOKEN=hf_your_token_here      # HuggingFace API token
HF_MODEL=Qwen/Qwen2.5-1.5B-Instruct
DEBUG=False
WEB_SEARCH_ENABLED=True
```

### Providers

- **`hf_api`** - HuggingFace Inference API (recommended for deployment)
- **`local`** - Local model on GPU (development only)
- **`openai`** - OpenAI API (not implemented yet)
- **`ollama`** - Ollama local server (not implemented yet)

## 🌐 Deployment

### Render (Free Tier)

```bash
# 1. Get HuggingFace token from https://huggingface.co/settings/tokens
# 2. Push to GitHub
git push origin main

# 3. Deploy via Render dashboard (detects render.yaml)
# 4. Add HF_TOKEN environment variable
# 5. Done! API is live
```

**Free tier includes:**
- ✅ 512MB RAM (sufficient with `hf_api` provider)
- ✅ Docker support
- ✅ Auto-deploy on push
- ⚠️ Sleeps after 15min (mitigated with keepalive)

See: [Deployment Guide](docs/deployment.md)

### Keepalive (Cold Start Prevention)

```bash
# Option 1: Self-hosted script
python keepalive.py

# Option 2: UptimeRobot (web service)
# Monitor: https://your-api.onrender.com/ping
# Interval: Every 14 minutes
```

See: [Cold Start Solutions](docs/cold-start-solutions.md)

## 🤝 Contributing

Contributions welcome! See [Roadmap](docs/roadmap.md) for planned features.

## 📄 License

MIT License - see LICENSE file

## 🔗 Links

- **Live API:** [Your Render URL]
- **Portfolio:** [mdimranhs.vercel.app](https://mdimranhs.vercel.app)
- **Documentation:** [docs/](docs/)

---

Built with ❤️ by [Md Imran Hossain](https://mdimranhs.vercel.app)
