# Customer Service Agents Demo — Backend Architecture

## Overview

A multi-agent customer service system for airlines, built on [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) + [ChatKit](https://openai.github.io/chatkit-js/). Multiple specialized agents collaborate as a team to handle airline-related user requests.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Agent Runtime | [openai-agents](https://pypi.org/project/openai-agents/) (Python) |
| Streaming Chat | [openai-chatkit](https://pypi.org/project/openai-chatkit/) |
| Web Framework | FastAPI + Uvicorn |
| Frontend | Next.js + ChatKit.js |
| Context | Pydantic (shared state model) |

---

## Directory Structure

```
python-backend/
├── main.py                  # FastAPI app entry, CORS, endpoints
├── server.py                # AirlineServer (ChatKit integration, event streaming)
├── memory_store.py          # In-memory thread storage
├── airline/
│   ├── agents.py            # 6 Agent definitions + handoff wiring
│   ├── tools.py             # @function_tool decorated async functions
│   ├── context.py           # AirlineAgentContext (shared state model)
│   ├── guardrails.py        # Relevance + Jailbreak guardrails
│   └── demo_data.py         # Mock itineraries (on_time, disrupted)
├── test_*.py                # Standalone test scripts
└── requirements.txt
```

---

## Agent Definitions

### 6 Specialized Agents (`agents.py`)

| Agent | Role | Tools |
|-------|------|-------|
| `triage_agent` | Entry point, routes to specialists | `get_trip_details` |
| `flight_information_agent` | Flight status, delay, connection risk | `flight_status_tool`, `get_matching_flights` |
| `booking_cancellation_agent` | Book, rebook, cancel flights | `cancel_flight`, `get_matching_flights`, `book_new_flight` |
| `seat_special_services_agent` | Seat changes, medical/front-row requests | `update_seat`, `assign_special_service_seat`, `display_seat_map` |
| `faq_agent` | Policy questions (baggage, Wi-Fi, compensation) | `faq_lookup_tool` |
| `refunds_compensation_agent` | Compensation cases, hotel/meal vouchers | `issue_compensation`, `faq_lookup_tool` |

Each agent is created via the `Agent[...]` SDK class:

```python
Agent[T](
    name="Agent Name",
    model=MODEL,                              # from env MODEL_NAME
    instructions="...system prompt...",        # what the agent does
    tools=[...],                              # callable functions
    handoffs=[...],                           # allowed next agents
    input_guardrails=[...],                   # safety checks
)
```

### Handoff Wiring (`agents.py:203-226`)

Agents are wired together explicitly:

```python
triage_agent.handoffs = [
    flight_information_agent,
    handoff(agent=booking_cancellation_agent, on_handoff=on_booking_handoff),
    handoff(agent=seat_special_services_agent, on_handoff=on_seat_booking_handoff),
    faq_agent,
    refunds_compensation_agent,
]
```

`on_handoff` callbacks populate missing context fields before the target agent runs (e.g., generate a random `confirmation_number` if none exists).

---

## Tools (`tools.py`)

Tools are async functions decorated with `@function_tool`. They receive a `RunContextWrapper[AirlineAgentChatContext]`, giving read/write access to the shared `AirlineAgentContext` state.

Key tools:

- `get_trip_details` — Reads user message, infers scenario (Paris→NY→Austin disrupted or FLT-123 on-time), hydrates context
- `flight_status_tool` — Returns mock flight status; streams `ProgressUpdateEvent` to UI
- `get_matching_flights` — Returns rebook options for disrupted itineraries
- `book_new_flight` — Updates context with new flight + auto-assigns seat
- `assign_special_service_seat` — Front-row/medical seat assignment
- `display_seat_map` — Returns `"DISPLAY_SEAT_MAP"` string to trigger UI widget
- `cancel_flight`, `update_seat`, `issue_compensation`, `faq_lookup_tool`, `baggage_tool`

Tool calls are **never written explicitly in code** — the LLM decides when to call them based on the `instructions` + `description_override` fields.

---

## Shared Context (`context.py`)

All agents share a single `AirlineAgentContext` (Pydantic model) that persists across the conversation:

```python
class AirlineAgentContext(BaseModel):
    passenger_name: str | None
    confirmation_number: str | None
    seat_number: str | None
    flight_number: str | None
    account_number: str | None
    itinerary: list[dict] | None        # internal only
    baggage_claim_id: str | None         # internal only
    compensation_case_id: str | None
    vouchers: list[str] | None
    special_service_note: str | None
    origin: str | None
    destination: str | None
```

The `public_context()` function filters out internal fields before sending state to the UI.

---

## Guardrails (`guardrails.py`)

Two input guardrails run on every user message before the main agent:

### Relevance Guardrail
- Uses a separate `guardrail_agent` (LLM call) to classify whether the user's message is airline-related
- `is_relevant = False` → tripwire triggered → agent refuses with "Sorry, I can only answer airline questions"

### Jailbreak Guardrail
- Detects prompt injection / system prompt leakage attempts
- `is_safe = False` → same refusal response

Guardrails are defined as `@input_guardrail` decorated async functions that run `Runner.run(guardrail_agent, prompt)`.

---

## Routing Mechanism

Routing is **LLM-driven, not hard-coded**.

1. User message enters `triage_agent`
2. Triage reads its `instructions` which describe routing rules
3. Triage's `handoffs` list restricts which agents it can choose from
4. LLM outputs a `handoff` structured output signal (SDK protocol)
5. SDK's `execute_handoffs()` in `turn_resolution.py` captures this signal
6. It calls `handoff.on_invoke_handoff()` — runs the user's `on_handoff` callback (fills in missing context fields)
7. Returns the target `Agent` instance
8. Run loop continues with the new agent

```python
# handoffs/__init__.py:278 — _invoke_handoff
async def _invoke_handoff(ctx, input_json=None) -> Agent:
    if on_handoff is not None:
        result = on_handoff(ctx)   # ← run callback (populate context)
        if inspect.isawaitable(result):
            await result
    return agent                   # ← return new agent
```

```python
# turn_resolution.py:443 — execute_handoffs
new_agent = await handoff.on_invoke_handoff(context_wrapper, tool_call.arguments)
# ... then run loop continues with new_agent
```

---

## AirlineServer (`server.py`)

`AirlineServer` extends `ChatKitServer` from the chatkit library. It bridges the Agents SDK with ChatKit's streaming protocol.

### ConversationState (per thread)

```python
@dataclass
class ConversationState:
    input_items: List[Any]                  # message history
    context: AirlineAgentContext             # shared context
    current_agent_name: str                  # active agent
    events: List[AgentEvent]                 # UI event log
    guardrails: List[GuardrailCheck]        # guardrail results
```

### respond() — main streaming handler

```python
async def respond(thread, input_user_message, context) -> AsyncIterator[ThreadStreamEvent]:
    state = _state_for_thread(thread.id)
    chat_context = AirlineAgentChatContext(thread=thread, store=store, state=state.context)
    
    result = Runner.run_streamed(current_agent, input_items, context=chat_context)
    async for event in stream_agent_response(chat_context, result):
        # Convert run items → AgentEvents → broadcast to UI
        yield event
```

### Key responsibilities

- **Event recording** (`_record_events`): Converts SDK `RunItem` objects (`MessageOutputItem`, `HandoffOutputItem`, `ToolCallItem`, `ToolCallOutputItem`) into `AgentEvent` for the UI panel
- **Broadcasting** (`_broadcast_state`): Pushes state deltas to WebSocket listeners (the Next.js frontend)
- **Guardrail handling**: Catches `InputGuardrailTripwireTriggered` → yields refusal message
- **Max turns**: Catches `MaxTurnsExceeded`

---

## API Endpoints (main.py)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/chatkit` | Main streaming chat endpoint |
| `GET` | `/chatkit/state` | Snapshot of thread state (agents, events, context, guardrails) |
| `GET` | `/chatkit/bootstrap` | Initial bootstrap state for new threads |
| `GET` | `/chatkit/state/stream` | SSE stream of state changes |
| `GET` | `/health` | Health check |

---

## Environment Configuration

| Variable | Default | Description |
|---------|---------|-------------|
| `OPENAI_API_KEY` | — | API key (OpenAI / MiniMax / Mimo / any compatible) |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | API base URL |
| `MODEL_NAME` | `gpt-4o` | Model name for main agents |
| `GUARDRAIL_MODEL_NAME` | `MODEL_NAME` | Separate model for guardrail agents |
| `OPENAI_TRACING_DISABLED` | `1` | Disable SDK tracing |

Config is loaded from `python-backend/.env` via a custom reader in `main.py` before any SDK imports. The `set_use_responses_by_default(False)` call forces use of the `chat/completions` API rather than the newer `responses` API.

---

## Data Flow Summary

```
User Input (HTTP/WebSocket)
    ↓
main.py:chatkit_endpoint → AirlineServer.respond()
    ↓
Runner.run_streamed(triage_agent, messages, context=chat_context)
    ↓
LLM decides: route / call tool / guardrail check
    ↓
SDK run loop: execute_handoffs() / tool functions / guardrails
    ↓
stream_agent_response() yields RunItems
    ↓
AirlineServer._record_events() converts to AgentEvent
    ↓
ClientEffectEvent → WebSocket → Next.js UI
    ↓
User sees agent flow + tool calls + context updates in real-time
```
