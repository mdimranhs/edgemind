/**
 * Production-grade client for EdgeMind API with cold start handling
 *
 * Features:
 * - Exponential backoff for cold starts
 * - User feedback during warmup
 * - Timeout handling
 * - Retry logic
 */

class EdgeMindClient {
  constructor(baseURL) {
    this.baseURL = baseURL;
    this.maxRetries = 3;
    this.coldStartTimeout = 90000; // 90s for Render cold start
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
   * Smart retry with cold start awareness
   */
  async chat(messages, options = {}) {
    const {
      stream = false,
      onWarmup = null,
      onRetry = null
    } = options;

    for (let attempt = 0; attempt < this.maxRetries; attempt++) {
      try {
        // Notify user on first attempt if cold start expected
        if (attempt === 0 && onWarmup) {
          onWarmup('Waking up API...');
        }

        const controller = new AbortController();
        const timeoutId = setTimeout(
          () => controller.abort(),
          this.coldStartTimeout
        );

        const response = await fetch(`${this.baseURL}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ messages, stream }),
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
        // Last attempt - throw error
        if (attempt === this.maxRetries - 1) {
          throw new Error(`API failed after ${this.maxRetries} attempts: ${error.message}`);
        }

        // Notify user about retry
        if (onRetry) {
          onRetry(attempt + 1, this.maxRetries);
        }

        // Exponential backoff before retry
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

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') return;
          try {
            yield JSON.parse(data);
          } catch (e) {
            console.warn('Failed to parse SSE:', data);
          }
        }
      }
    }
  }

  /** Service health check. */
  async health() {
    try {
      const response = await fetch(`${this.baseURL}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000), // Quick timeout
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  /**
   * Pre-warm the API before user interaction
   * Call this on page load, mouse hover, or tab focus
   */
  async prewarm() {
    try {
      await this.ping();
      return true;
    } catch {
      return false;
    }
  }
}

// ============================================
// Usage Examples
// ============================================

// Example 1: Basic chat with cold start handling
async function basicExample() {
  const client = new EdgeMindClient('https://edgemind-api.onrender.com');

  try {
    const response = await client.chat(
      [{ role: 'user', content: 'Hello!' }],
      {
        onWarmup: (msg) => console.log('🔄', msg),
        onRetry: (attempt, max) => console.log(`⏳ Retry ${attempt}/${max}...`)
      }
    );
    console.log('✅', response);
  } catch (error) {
    console.error('❌', error.message);
  }
}

// Example 2: Streaming with UI feedback
async function streamingExample() {
  const client = new EdgeMindClient('https://edgemind-api.onrender.com');

  const statusDiv = document.getElementById('status');
  const outputDiv = document.getElementById('output');

  try {
    const stream = await client.chat(
      [{ role: 'user', content: 'Explain RAG' }],
      {
        stream: true,
        onWarmup: (msg) => {
          statusDiv.textContent = msg;
          statusDiv.className = 'warming';
        },
        onRetry: (attempt, max) => {
          statusDiv.textContent = `Retrying... ${attempt}/${max}`;
        }
      }
    );

    statusDiv.textContent = 'Connected ✓';
    statusDiv.className = 'success';

    for await (const chunk of stream) {
      outputDiv.textContent += chunk.token || '';
    }
  } catch (error) {
    statusDiv.textContent = `Error: ${error.message}`;
    statusDiv.className = 'error';
  }
}

// Example 3: Proactive pre-warming strategies
class SmartUI {
  constructor(apiURL) {
    this.client = new EdgeMindClient(apiURL);
    this.setupPrewarming();
  }

  setupPrewarming() {
    // Strategy 1: Pre-warm on page load (background)
    window.addEventListener('load', () => {
      this.client.prewarm();
    });

    // Strategy 2: Pre-warm on input focus (user intent signal)
    document.getElementById('chatInput')?.addEventListener('focus', () => {
      this.client.prewarm();
    });

    // Strategy 3: Pre-warm on mouse hover over send button
    document.getElementById('sendBtn')?.addEventListener('mouseenter', () => {
      this.client.prewarm();
    }, { once: true });

    // Strategy 4: Pre-warm on tab visibility change
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) {
        this.client.prewarm();
      }
    });
  }
}

// Export for use in your frontend
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { EdgeMindClient };
}
