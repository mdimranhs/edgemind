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
| `session_id` | string | `"default"` | Conversation session ID for memory isolation |
| `messages` | array[ChatMessage] | `[]` | Messages for this turn (typically 1 user message) |
| `stream` | boolean | `false` | If `true`, returns SSE stream instead of JSON |

### ChatMessage

```json
{"role": "user", "content": "Hello"}
```

- `role`: `"system"` | `"user"` | `"assistant"`
- `content`: string

### Response (non-streaming)

```json
{
  "session_id": "default",
  "reply": "Hello! How can I assist you today?"
}
```

### Response (streaming)

When `stream: true`, returns `text/event-stream` with tokens delivered progressively:

```
Hel
lo
! How
 can
 I
 ...
```

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
