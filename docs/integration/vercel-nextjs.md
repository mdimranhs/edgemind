# Vercel + Next.js Integration

Complete guide for integrating EdgeMind API with Next.js apps on Vercel.

**For:** Portfolio sites like [mdimranhs.vercel.app](https://mdimranhs.vercel.app)

## Architecture

```
User → Vercel (Next.js) → Railway (EdgeMind API)
        ↓ (API Route)       ↓ (FastAPI)
        Edge Function       HuggingFace API
```

**Why this setup:**
- Hide API URL from client
- Add authentication layer
- Handle errors gracefully

---

## Setup

### 1. Environment Variables

Create `.env.local` in your Next.js project:

```bash
# .env.local
EDGEMIND_API_URL=https://edgemind-production-6ae2.up.railway.app
```

### 2. Create API Route (Proxy)

**File:** `app/api/chat/route.ts` (App Router) or `pages/api/chat.ts` (Pages Router)

#### App Router (Next.js 13+)

```typescript
// app/api/chat/route.ts
import { NextRequest, NextResponse } from 'next/server';

const API_URL = process.env.EDGEMIND_API_URL;

export const runtime = 'edge';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(60000),
    });

    if (!response.ok) {
      throw new Error(`API responded with ${response.status}`);
    }

    if (body.stream) {
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
        yield chunk;
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

1. **Add environment variable in Vercel dashboard:**
   - Variable: `EDGEMIND_API_URL`
   - Value: `https://edgemind-production-6ae2.up.railway.app`

2. **Deploy:**
   ```bash
   vercel deploy
   ```

---

## Production Checklist

- [ ] API URL in environment variable (not hardcoded)
- [ ] Error handling for API failures
- [ ] Retry logic in API route
- [ ] User feedback during loading
- [ ] Session management implemented

---

## Next Steps

- [See React component example](./react-example.jsx)
- [Review API documentation](../api.md)
