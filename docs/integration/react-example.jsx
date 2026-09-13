/**
 * EdgeMind Chat Component
 *
 * React component with:
 * - Streaming support
 * - Session management
 * - Accessible UI
 *
 * Usage:
 *   import { EdgeMindChat } from './EdgeMindChat';
 *   <EdgeMindChat apiUrl="https://edgemind-production-6ae2.up.railway.app" />
 */

import React, { useState, useRef, useEffect } from 'react';

export function EdgeMindChat({
  apiUrl = '/api/chat',
  sessionId = 'default',
  placeholder = 'Ask me anything...',
}) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function sendMessage() {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    const conversationMessages = [...messages, userMessage];

    setMessages(conversationMessages);
    setInput('');
    setStatus('loading');
    setError(null);

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          messages: conversationMessages,
          stream: true,
        }),
        signal: AbortSignal.timeout(60000),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      setStatus('streaming');
      let reply = '';

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        reply += chunk;

        setMessages(prev => [
          ...prev.slice(0, -1),
          { role: 'assistant', content: reply }
        ]);
      }

      setStatus('idle');

    } catch (error) {
      console.error('Chat error:', error);
      setStatus('error');
      setError('Failed to get response. Please try again.');
      setMessages(prev => prev.slice(0, -1));
    }
  }

  return (
    <div className="edgemind-chat" style={styles.container}>
      <div className="messages" style={styles.messages}>
        {messages.length === 0 && (
          <div style={styles.emptyState}>
            <p>Hi! I'm EdgeMind AI.</p>
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

        {status === 'loading' && (
          <div style={styles.statusMessage}>
            Thinking...
          </div>
        )}

        {status === 'streaming' && (
          <div style={styles.statusMessage}>
            <span className="typing-indicator">...</span>
          </div>
        )}

        {status === 'error' && error && (
          <div style={{ ...styles.statusMessage, color: '#e74c3c' }}>
            {error}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div style={styles.inputArea}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
          placeholder={placeholder}
          disabled={status === 'loading' || status === 'streaming'}
          style={styles.input}
          aria-label="Chat input"
        />
        <button
          onClick={sendMessage}
          disabled={status === 'loading' || status === 'streaming' || !input.trim()}
          style={styles.button}
          aria-label="Send message"
        >
          Send
        </button>
      </div>

      <style>{`
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
  },
};

export default function ExamplePage() {
  return (
    <div>
      <h1>Chat with EdgeMind</h1>
      <EdgeMindChat
        apiUrl="https://edgemind-production-6ae2.up.railway.app/chat"
        sessionId="demo-session"
        placeholder="Type your message..."
      />
    </div>
  );
}
