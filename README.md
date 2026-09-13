# EdgeMind 🧠

Production-ready AI assistant backend powered by FastAPI and HuggingFace. Deploy as a containerized service on AWS with streaming, RAG, and conversation memory.

## ✨ Features

- **🚀 Deployment ready** — Docker image ready for Amazon ECR and ECS Express Mode
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
- **Deployment:** Docker / Amazon ECR / ECS Express Mode / Vercel-ready

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
# Deploy to AWS
docker build --platform linux/amd64 -t edgemind-api .

# Use from anywhere
curl https://your-ecs-endpoint/chat -d '...'
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
| AWS container deployment | 🚧 In progress |
| Cloud database and vector store | 🚧 Planned |
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

- **Live API:** Configure after the ECS deployment
- **Portfolio:** [mdimranhs.vercel.app](https://mdimranhs.vercel.app)
- **Documentation:** [docs/](docs/)

---

Built with ❤️ by [Md Imran Hossain](https://mdimranhs.vercel.app)
