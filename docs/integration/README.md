# Integration Guide

Connect your frontend to EdgeMind API.

## Quick Start

```javascript
const response = await fetch('https://edgemind-production-6ae2.up.railway.app/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    messages: [{ role: 'user', content: 'Hello!' }]
  })
});

const data = await response.json();
console.log(data.reply);
```

## Available Integrations

### 📱 [Vercel + Next.js](./vercel-nextjs.md)
Complete guide for integrating with Next.js apps deployed on Vercel.
**Use this if:** Your portfolio is built with Next.js (like mdimranhs.vercel.app)

### ⚛️ [React Component](./react-example.jsx)
Ready-to-use React component with chat UI, streaming, and session management.
**Use this if:** You want a drop-in chat widget

### 🔧 [JavaScript Client](./client-example.js)
Production-ready client with retry logic, streaming, and timeout handling.
**Use this if:** You need low-level control or vanilla JavaScript

## Core Concepts

### 1. **Session Management**
```javascript
// Each user gets their own conversation history
const session_id = `user_${userId}`;

fetch('/chat', {
  body: JSON.stringify({
    session_id,  // Isolates conversations
    messages: [...]
  })
});
```

### 2. **Streaming for Better UX**
```javascript
// Enable streaming to show tokens as they arrive
const response = await fetch('/chat', {
  body: JSON.stringify({
    messages: [...],
    stream: true  // Returns Server-Sent Events
  })
});

// Read SSE stream
const reader = response.body.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  console.log(new TextDecoder().decode(value));
}
```

## Environment Variables

```bash
# Frontend .env.local
NEXT_PUBLIC_API_URL=https://edgemind-production-6ae2.up.railway.app
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat` | POST | Send messages, get AI responses |
| `/health` | GET | Check API health |
| `/docs` | GET | Interactive API documentation |
| `/` | GET | Root health check |

See [API Reference](../api.md) for detailed specs.

## Examples by Framework

- **Next.js App Router:** [vercel-nextjs.md](./vercel-nextjs.md)
- **React (any setup):** [react-example.jsx](./react-example.jsx)
- **Vanilla JS:** [client-example.js](./client-example.js)
- **Vue/Svelte:** Use the vanilla JS client as reference

## Best Practices

### ✅ Do
- Use streaming for better perceived performance
- Implement retry logic for transient failures
- Show user feedback during loading
- Use unique session IDs per user
- Handle errors gracefully

### ❌ Don't
- Store API responses in state without error handling
- Send entire conversation history every time (backend tracks it)
- Expose API URL directly in client (use Next.js API routes as proxy)

## Troubleshooting

### API not responding (>30s)
**Cause:** Model cold start or provider overload
**Fix:** Implement retry logic with exponential backoff

### CORS errors
**Cause:** Backend CORS not configured for your domain
**Fix:** Add your domain to backend CORS settings (or use Next.js API route as proxy)

### Conversation not persisting
**Cause:** Not sending `session_id`
**Fix:** Include `session_id` in every request

## Need Help?

- [API Documentation](../api.md)
- [Architecture Overview](../architecture.md)
- [Deployment Guide](../deployment.md)
