/**
 * Example client for the EdgeMind API
 *
 * Features:
 * - Exponential backoff with retry
 * - Timeout handling
 * - Streaming support
 * - Health check
 */

class EdgeMindClient {
  constructor(baseURL, sessionId = globalThis.crypto?.randomUUID?.() || `session_${Date.now()}`) {
    this.baseURL = baseURL;
    this.sessionId = sessionId;
    this.maxRetries = 3;
    this.timeout = 60000; // 60s
  }

  /**
   * Exponential backoff with jitter
   */
  async sleep(attempt) {
    const baseDelay = 2000;
    const maxDelay = 30000;
    const exponential = Math.min(baseDelay * Math.pow(2, attempt), maxDelay);
    const jitter = Math.random() * 1000;
    await new Promise(resolve => setTimeout(resolve, exponential + jitter));
  }

  /**
   * Smart retry with backoff
   */
  async chat(messages, options = {}) {
    const {
      stream = false,
      sessionId = this.sessionId,
      onRetry = null
    } = options;

    for (let attempt = 0; attempt < this.maxRetries; attempt++) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        const response = await fetch(`${this.baseURL}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ messages, session_id: sessionId, stream }),
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        if (stream) {
          return this._handleStream(response);
        }

        return await response.json();

      } catch (error) {
        if (attempt === this.maxRetries - 1) {
          throw new Error(`API failed after ${this.maxRetries} attempts: ${error.message}`);
        }

        if (onRetry) {
          onRetry(attempt + 1, this.maxRetries);
        }

        await this.sleep(attempt);
      }
    }
  }

  /**
   * Handle SSE streaming response
   */
  async *_handleStream(response) {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
      const events = buffer.split('\n\n');
      buffer = events.pop() || '';

      for (const event of events) {
        const data = event.split('\n').find(line => line.startsWith('data: '))?.slice(6);
        if (!data) continue;
        if (data === '[DONE]') return;
        const payload = JSON.parse(data);
        if (payload.error) throw new Error(payload.error.message || 'Chat generation failed');
        const token = payload.choices?.[0]?.delta?.content;
        if (typeof token === 'string') yield token;
      }

      if (done) break;
    }
  }

  /**
   * Service health check
   */
  async health() {
    try {
      const response = await fetch(`${this.baseURL}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000),
      });
      return response.ok;
    } catch {
      return false;
    }
  }
}

// ============================================
// Usage Examples
// ============================================

// Example 1: Basic chat
async function basicExample() {
  const client = new EdgeMindClient('https://edgemind-production-6ae2.up.railway.app');

  try {
    const response = await client.chat(
      [{ role: 'user', content: 'Hello!' }],
      {
        onRetry: (attempt, max) => console.log(`Retry ${attempt}/${max}...`)
      }
    );
    console.log(response);
  } catch (error) {
    console.error(error.message);
  }
}

// Example 2: Streaming
async function streamingExample() {
  const client = new EdgeMindClient('https://edgemind-production-6ae2.up.railway.app');

  try {
    const stream = await client.chat(
      [{ role: 'user', content: 'Explain RAG' }],
      { stream: true }
    );

    for await (const chunk of stream) {
      process.stdout.write(chunk);
    }
  } catch (error) {
    console.error(error.message);
  }
}

// Export for use in your frontend
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { EdgeMindClient };
}
