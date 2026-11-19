# API Reference

## POST /chat

Send a message to EdgeMind and get a response.

### Request Body

```json
{
  "session_id": "default",
  "messages": [{"role": "user", "content": "Hello"}],
  "stream": false
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `session_id` | string | `"default"` | Session key used only when `MEMORY_BACKEND=sqlite`; ignored in stateless mode |
| `messages` | array[ChatMessage] | required | Recent conversation turns, ending with a user message |
| `stream` | boolean | `false` | If `true`, returns a Server-Sent Events stream |

### ChatMessage

```json
{"role": "user", "content": "Hello"}
```

- `role`: `"user"` | `"assistant"`; clients cannot provide system messages
- `content`: string

### Response (non-streaming)

```json
{
  "session_id": "default",
  "reply": "Hello! How can I assist you today?"
}
```

### Response (streaming)

When `stream: true`, returns `text/event-stream` using OpenAI-compatible delta events, followed by `[DONE]`:

```
data: {"choices":[{"delta":{"content":"Hello"}}]}

data: {"choices":[{"delta":{"content":"!"}}]}

data: [DONE]

```

Stream errors use an `event: error` event with an OpenAI-compatible JSON `error.message` field. The HTTP status cannot change after streaming has started.

## GET /

Root health check.

```json
{"message": "Welcome to EdgeMind 🚀"}
```

## GET /health

Service health check for load balancers and monitoring.

```json
{"status": "healthy", "service": "EdgeMind API"}
```
