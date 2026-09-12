# Vercel + Next.js Integration

Complete guide for integrating EdgeMind API with Next.js apps on Vercel.

**For:** Portfolio sites like [mdimranhs.vercel.app](https://mdimranhs.vercel.app)

## Architecture

```
User → Vercel (Next.js) → Render (EdgeMind API)
        ↓ (API Route)       ↓ (FastAPI)
        Edge Function       HuggingFace API
```

**Why this setup:**
- ✅ Hide API URL from client
- ✅ Add authentication layer
- ✅ Handle cold starts gracefully
- ✅ Pre-warm API from edge

---

## Setup

### 1. Environment Variables

Create `.env.local` in your Next.js project:

```bash
# .env.local
EDGEMIND_API_URL=https://edgemind-api.onrender.com
```

### 2. Create API Route (Proxy)

**File:** `app/api/chat/route.ts` (App Router) or `pages/api/chat.ts` (Pages Router)

#### App Router (Next.js 13+)

```typescript
// app/api/chat/route.ts
import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.EDGEMIND_API_URL;

export const runtime = 'edge'; // Optional: run on edge for lower latency

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      // Increase timeout for cold starts
      signal: AbortSignal.timeout(90000), // 90s
    });

    if (!response.ok) {
      throw new Error(`API responded with ${response.status}`);
    }

    // Stream or JSON based on request
    if (body.stream) {
      // Pass through SSE stream
      return new NextResponse(response.body, {
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
      });
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('Chat API error:', error);
    return NextResponse.json(
      { error: 'Failed to connect to AI service' },
      { status: 500 }
    );
  }
}
```

#### Pages Router (Next.js 12)

```typescript
// pages/api/chat.ts
import type { NextApiRequest, NextApiResponse } from 'next';

const API_URL = process.env.EDGEMIND_API_URL;

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body),
    });

    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ error: 'AI service unavailable' });
  }
}
```

### 3. Pre-warm API (Background)

Create a background pre-warm function to avoid cold starts:

```typescript
// lib/prewarm-api.ts
export async function prewarmAPI() {
  try {
    await fetch(`${process.env.EDGEMIND_API_URL}/ping`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000),
    });
  } catch {
    // Silently fail - it's just a pre-warm
  }
}
```

Call it in your root layout:

```typescript
// app/layout.tsx
import { prewarmAPI } from '@/lib/prewarm-api';

export default function RootLayout({ children }) {
  // Pre-warm in background on page load
  if (typeof window !== 'undefined') {
    prewarmAPI();
  }

  return <html>{children}</html>;
}
```

---

## Client Component

### React Hook for Chat

```typescript
// hooks/useEdgeMind.ts
import { useState } from 'react';

export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export function useEdgeMind(sessionId = 'default') {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function chat(messages: Message[]) {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          messages,
          stream: false,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      return data.reply;

    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }

  return { chat, loading, error };
}
```

### Chat Component

```tsx
// components/ChatWidget.tsx
'use client';

import { useState } from 'react';
import { useEdgeMind, type Message } from '@/hooks/useEdgeMind';

export function ChatWidget() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const { chat, loading, error } = useEdgeMind('portfolio-visitor');

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      const reply = await chat([...messages, userMessage]);
      setMessages(prev => [...prev, { role: 'assistant', content: reply }]);
    } catch (err) {
      console.error('Chat error:', err);
    }
  };

  return (
    <div className="chat-widget">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
        {loading && <div className="loading">Thinking...</div>}
        {error && <div className="error">{error}</div>}
      </div>

      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask me anything..."
          disabled={loading}
        />
        <button onClick={handleSend} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
}
```

---

## Streaming Implementation

For real-time token streaming:

```typescript
// hooks/useEdgeMindStream.ts
import { useState } from 'react';

export function useEdgeMindStream() {
  const [streaming, setStreaming] = useState(false);

  async function* chatStream(messages: Message[]) {
    setStreaming(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages,
          stream: true,
        }),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') return;
            yield data;
          }
        }
      }
    } finally {
      setStreaming(false);
    }
  }

  return { chatStream, streaming };
}
```

**Usage:**
```tsx
const { chatStream } = useEdgeMindStream();

const handleSendStream = async () => {
  let reply = '';
  for await (const token of chatStream(messages)) {
    reply += token;
    // Update UI in real-time
    setMessages(prev => [...prev.slice(0, -1), {
      role: 'assistant',
      content: reply
    }]);
  }
};
```

---

## Deployment

### Vercel Configuration

No special config needed! Just:

1. **Add environment variable in Vercel dashboard:**
   - Variable: `EDGEMIND_API_URL`
   - Value: `https://edgemind-api.onrender.com`

2. **Deploy:**
   ```bash
   vercel deploy
   ```

### Cold Start Handling on Vercel

Since Vercel Edge Functions are always warm, they can handle Render cold starts:

```typescript
// app/api/chat/route.ts
export async function POST(request: NextRequest) {
  const maxRetries = 3;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        body: JSON.stringify(await request.json()),
        signal: AbortSignal.timeout(90000),
      });
      
      return new NextResponse(response.body);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(r => setTimeout(r, 2000 * Math.pow(2, i)));
    }
  }
}
```

---

## Example: Portfolio Integration

For a portfolio site like **mdimranhs.vercel.app**:

```tsx
// app/portfolio/page.tsx
import { ChatWidget } from '@/components/ChatWidget';

export default function PortfolioPage() {
  return (
    <div>
      <h1>Md Imran Hossain</h1>
      <p>Software Engineer | AI Enthusiast</p>
      
      {/* Chat widget powered by EdgeMind */}
      <ChatWidget />
    </div>
  );
}
```

**Initialize with context:**
```typescript
const { chat } = useEdgeMind('portfolio-visitor');

// Pre-load context about you
useEffect(() => {
  chat([{
    role: 'system',
    content: 'You are an AI assistant on Md Imran Hossain\'s portfolio. Help visitors learn about his work.'
  }]);
}, []);
```

---

## Performance Tips

### 1. Pre-warm on Hover
```tsx
<button
  onMouseEnter={() => fetch('/api/chat', { method: 'HEAD' })}
  onClick={handleSend}
>
  Send
</button>
```

### 2. Debounce Typing Indicators
```typescript
const [isTyping, setIsTyping] = useState(false);

useEffect(() => {
  const timer = setTimeout(() => setIsTyping(false), 500);
  return () => clearTimeout(timer);
}, [input]);
```

### 3. Cache Common Questions
Use Vercel KV or localStorage:
```typescript
const cached = await kv.get(`answer:${question}`);
if (cached) return cached;
```

---

## Troubleshooting

### Cold Start Timeout
**Symptom:** Request times out after 10s  
**Fix:** Increase timeout to 90s in API route

### CORS Errors
**Symptom:** Network error in browser console  
**Fix:** You shouldn't get CORS errors since you're using Next.js API route as proxy

### Session Not Persisting
**Symptom:** AI forgets previous messages  
**Fix:** Ensure consistent `session_id` across requests

---

## Production Checklist

- [ ] API URL in environment variable (not hardcoded)
- [ ] Error handling for cold starts
- [ ] Pre-warming on page load
- [ ] Retry logic in API route
- [ ] User feedback during loading
- [ ] Session management implemented
- [ ] Analytics tracking (optional)

---

## Next Steps

- [See React component example](./react-example.jsx)
- [Learn about cold start solutions](../cold-start-solutions.md)
- [Review API documentation](../api.md)
