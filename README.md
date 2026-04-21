# Simple agent server in python

Concepts:
- agent.py - agent abstraction containing orchestraction logic
- llm_provider.py - interface to connect various providers
    - this contains streaming example as well, although it's not yet propagated upstream to the endpoint
- tools.py - interface for tools, allowing uniform handling

# Setup

1. Install basic dependencies through

```bash
uv sync
```

2. Copy `.env.example` into `.env` and fill in credentials

3. Run code with 
```bash
uv run uvicorn main:app --reload
```

4. It exposes an endpoint to chat with LLM through:
```bash
  curl -X POST http://127.0.0.1:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "hello"}'
```

5. (Optional) There's a reference git submodule under reference/original that can be downloaded with. This is the https://github.com/Miehau/ai-assistant repository
```bash
git submodule update --init --recursive
```

> Note: currently it contains only single example tool `Horoscope` and does not yet loop back outcome

There's also async endpoint I didn't have time yet to consolidate `/chat_async`