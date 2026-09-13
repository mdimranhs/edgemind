/**
 * EdgeMind Chat Component
 *
 * Production-ready React component with:
 * - Streaming support
 * - Cold start handling with retry
 * - User feedback during warmup
 * - Session management
 * - Accessible UI
 *
 * Usage:
 *   import { EdgeMindChat } from './EdgeMindChat';
 *   <EdgeMindChat apiUrl="https://your-api.onrender.com" />
 */

import React, { useState, useRef, useEffect } from 'react';

export function EdgeMindChat({
  apiUrl = '/api/chat',  // Use Next.js proxy by default
  sessionId = 'default',
  placeholder = 'Ask me anything...',
  systemPrompt = null,
}) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [status, setStatus] = useState('idle'); // idle | loading | streaming | error
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);


  async function sendMessage(retryCount = 0) {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    const conversationMessages = [...messages, userMessage];

    setMessages(conversationMessages);
    setInput('');
    setStatus('loading');
    setError(null);

    // Build request messages
    const requestMessages = systemPrompt
      ? [{ role: 'system', content: systemPrompt }, ...conversationMessages]
      : conversationMessages;

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          messages: requestMessages,
          stream: true,
        }),
        signal: AbortSignal.timeout(90000), // 90s for cold starts
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      // Stream response
      setStatus('streaming');
      let reply = '';

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      // Add empty assistant message that we'll fill
      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        reply += chunk;

        // Update last message (assistant's reply)
        setMessages(prev => [
          ...prev.slice(0, -1),
          { role: 'assistant', content: reply }
        ]);
      }

      setStatus('idle');

    } catch (error) {
      console.error('Chat error:', error);

      // Retry logic for cold starts
      if (retryCount < 2) {
        setStatus('loading');
        setError(`Waking up API... (retry ${retryCount + 1}/2)`);

        await new Promise(r => setTimeout(r, 2000 * Math.pow(2, retryCount)));
        return sendMessage(retryCount + 1);
      }

      // Final failure
      setStatus('error');
      setError('Failed to get response. Please try again.');

      // Remove the failed user message
      setMessages(prev => prev.slice(0, -1));
    }
  }

  return (
    <div className="edgemind-chat" style={styles.container}>
      {/* Messages */}
      <div className="messages" style={styles.messages}>
        {messages.length === 0 && (
          <div style={styles.emptyState}>
            <p>👋 Hi! I'm EdgeMind AI.</p>
            <p>Ask me anything!</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              ...styles.message,
              ...(msg.role === 'user' ? styles.userMessage : styles.assistantMessage),
            }}
          >
            <strong>{msg.role === 'user' ? 'You' : 'EdgeMind'}:</strong>
            <p>{msg.content}</p>
          </div>
        ))}

        {/* Status indicators */}
        {status === 'loading' && (
          <div style={styles.statusMessage}>
            <span className="loading-dots">Thinking</span>
            {error && <small style={{ color: '#888' }}>{error}</small>}
          </div>
        )}

        {status === 'streaming' && (
          <div style={styles.statusMessage}>
            <span className="typing-indicator">●●●</span>
          </div>
        )}

        {status === 'error' && error && (
          <div style={{ ...styles.statusMessage, color: '#e74c3c' }}>
            ⚠️ {error}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={styles.inputArea}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
          onFocus={prewarmAPI} // Pre-warm on focus
          placeholder={placeholder}
          disabled={status === 'loading' || status === 'streaming'}
          style={styles.input}
          aria-label="Chat input"
        />
        <button
          onClick={() => sendMessage()}
          onMouseEnter={prewarmAPI} // Pre-warm on hover
          disabled={status === 'loading' || status === 'streaming' || !input.trim()}
          style={styles.button}
          aria-label="Send message"
        >
          {status === 'loading' || status === 'streaming' ? '⏳' : '📤'}
        </button>
      </div>

      {/* CSS animations */}
      <style>{`
        .loading-dots::after {
          content: '...';
          animation: dots 1.5s steps(3, end) infinite;
        }
        @keyframes dots {
          0%, 20% { content: '.'; }
          40% { content: '..'; }
          60%, 100% { content: '...'; }
        }
        .typing-indicator {
          animation: blink 1.4s infinite;
        }
        @keyframes blink {
          0%, 100% { opacity: 0.2; }
          50% { opacity: 1; }
        }
      `}</style>
    </div>
  );
}

// Inline styles (replace with CSS modules or Tailwind in production)
const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '500px',
    maxWidth: '600px',
    margin: '0 auto',
    border: '1px solid #ddd',
    borderRadius: '8px',
    overflow: 'hidden',
    fontFamily: 'system-ui, sans-serif',
  },
  messages: {
    flex: 1,
    overflowY: 'auto',
    padding: '1rem',
    backgroundColor: '#f9f9f9',
  },
  emptyState: {
    textAlign: 'center',
    color: '#888',
    marginTop: '4rem',
  },
  message: {
    marginBottom: '1rem',
    padding: '0.75rem',
    borderRadius: '8px',
    maxWidth: '80%',
  },
  userMessage: {
    backgroundColor: '#007bff',
    color: 'white',
    marginLeft: 'auto',
    textAlign: 'right',
  },
  assistantMessage: {
    backgroundColor: 'white',
    color: '#333',
    border: '1px solid #eee',
  },
  statusMessage: {
    textAlign: 'center',
    color: '#666',
    padding: '0.5rem',
    fontSize: '0.9rem',
  },
  inputArea: {
    display: 'flex',
    padding: '1rem',
    backgroundColor: 'white',
    borderTop: '1px solid #ddd',
  },
  input: {
    flex: 1,
    padding: '0.75rem',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '1rem',
    outline: 'none',
  },
  button: {
    marginLeft: '0.5rem',
    padding: '0.75rem 1.5rem',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '1rem',
    transition: 'opacity 0.2s',
  },
};

// Example usage in a Next.js page
export default function ExamplePage() {
  return (
    <div>
      <h1>Chat with EdgeMind</h1>
      <EdgeMindChat
        apiUrl="/api/chat"
        sessionId="demo-session"
        placeholder="Type your message..."
        systemPrompt="You are a helpful assistant on a developer's portfolio."
      />
    </div>
  );
}
