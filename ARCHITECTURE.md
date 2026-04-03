# Architecture

## Pattern Overview

Civitas follows a **layered async pipeline** architecture. The world is a discrete-state machine
that advances in ticks. Each tick is driven by an async scheduler that fires all agent cognitive
pipelines concurrently, collects their resulting actions, then resolves those actions against the
world in a single synchronous arbitration pass. This separates LLM latency (parallelised across
all agents) from world physics (deterministic and sequential).

The pattern is inspired by PIANO (Parallel Information Aggregation via Neural Orchestration) from
Project Sid: a fast loop that emits actions from cached intentions, and a slow loop that calls the
LLM only when meaningful new information warrants a re-plan. In Civitas this maps to Mesa's step
cycle (fast, every tick) and the async LLM pipeline (slow, triggered by importance threshold or
timer).

Mesa 3 provides the world substrate — grid spaces, agent registry, DataCollector — and Civitas
replaces Mesa's synchronous scheduler with an `asyncio`-based tick engine. All world physics runs
in the Mesa model's synchronous resolution pass; all LLM calls run concurrently in the async
event loop.

```
┌──────────────────────────────────────────────────────────────┐
│  Web UI  (React + Vite)                                       │
├──────────────────────────────────────────────────────────────┤
│  REST API + WebSocket  (FastAPI)                              │
├──────────────────────────────────────────────────────────────┤
│  Simulation Core  (Mesa model + async tick engine)            │
│  ┌───────────┐  ┌──────────┐  ┌───────────┐  ┌───────────┐  │
│  │ WorldGen  │  │ EnvLayer │  │TickEngine │  │  GodMode  │  │
│  └───────────┘  └──────────┘  └───────────┘  └───────────┘  │
│  ┌───────────┐  ┌──────────┐  ┌───────────┐  ┌───────────┐  │
│  │ Arbiter   │  │ Ablation │  │ EventBus  │  │  Logger   │  │
│  └───────────┘  └──────────┘  └───────────┘  └───────────┘  │
├──────────────────────────────────────────────────────────────┤
│  Agent Layer  (modular cognitive pipeline, one per agent)     │
│  ┌────────┐ ┌────────┐ ┌───────────┐ ┌────────┐ ┌────────┐  │
│  │Percept │ │ Memory │ │Reflection │ │Planner │ │ Tools  │  │
│  └────────┘ └────────┘ └───────────┘ └────────┘ └────────┘  │
│  ┌────────┐ ┌────────┐                                        │
│  │ Comms  │ │Identity│                                        │
│  └────────┘ └────────┘                                        │
├──────────────────────────────────────────────────────────────┤
│  LLM Backends  (Claude · OpenAI · local · mock)               │
├──────────────────────────────────────────────────────────────┤
│  Persistence  (SQLite via aiosqlite)                          │
└──────────────────────────────────────────────────────────────┘
```

---

## Layers

### 1. Web UI

React + Vite single-page application. Communicates with the backend over REST for lifecycle
operations and WebSocket for streaming tick updates. Contains no simulation logic. All UI
state is derived from server events.

Panels:
- **World viewport** — tile grid rendered as a canvas with switchable overlays (faction,
  resource density, health, wealth, action arrows)
- **Agent inspector** — click any agent to see its memory stream, current plan tree, last
  N LLM prompts/responses, and action history
- **God controls** — free-text NL commands and a structured event palette (drought, plague,
  earthquake, spawn resource, kill agent)
- **Experiment panel** — ablation flag toggles per-agent or globally, importable/exportable
  config JSON, per-run notes field
- **Timeline scrubber** — seek to any stored snapshot, control playback speed, step forward
  one tick at a time

### 2. REST API and WebSocket

FastAPI application. Stateless — all truth lives in the simulation registry and SQLite.
Exposes the full OpenAPI surface documented in `openapi.yaml`.

Routers:
- `router/sim.py` — simulation CRUD and lifecycle (create, start, pause, stop, reset, delete)
- `router/world.py` — world state reads (full snapshot, tile detail, resource layer)
- `router/agents.py` — agent reads (list, detail, memory, plan, action history)
- `router/events.py` — structured event injection and NL god-mode commands
- `router/ablation.py` — read and write ablation configuration per simulation
- `router/replay.py` — list snapshots, seek to tick, activate replay mode
- `router/stats.py` — token usage, tick durations, agent activity metrics
- `ws/tick.py` — WebSocket endpoint that streams tick-diff events to all subscribers

### 3. Simulation Core

The Mesa `CivModel` subclass and all infrastructure that drives it.

**World generation** (`core/worldgen/`): Procedural terrain via `pynoise`. A `NoiseStack`
composes Perlin noise (base terrain) with Ridged Multifractal (mountain ridges) and Billow
(plains variation) to produce a heightmap. A separate moisture pass uses Perlin at a
different frequency and offset. Biomes are assigned by thresholding the (height, moisture)
pair against a biome table. Resources are seeded per biome with configurable density and
cluster parameters. The full generator is seeded — same seed + same config always produces
identical terrain.

**Environment layer** (`core/env/`): The dynamic world state on top of static terrain.
Resource nodes regenerate at biome-specific rates and deplete when harvested. Weather events
(drought, flood, frost, abundance) modify regeneration rates for a configurable duration.
The environment layer exposes a read-only interface (`EnvReader`) to agent perception and a
write interface (`EnvWriter`) exclusively to the action resolution pass, enforcing the
invariant that agents never mutate world state directly.

**Tick engine** (`core/engine.py`): The async scheduler and the main simulation loop.
Runs as a long-lived `asyncio.Task`. On each tick: snapshot world → scatter agent steps →
gather actions → arbitrate → apply → log → broadcast.

**Action arbiter** (`core/arbiter.py`): Resolves conflicts from concurrent actions before
any mutation touches the Mesa grid. Handles movement collisions, resource contention,
trade matching, and attack vs build conflicts. Priority ordering is configurable (random
shuffle by default) and logged per tick for reproducibility.

**Event bus** (`core/eventbus.py`): In-process pub/sub. Events are `(tick, type, payload)`
named tuples. Publishers: god mode, arbiter (conflict events), environment (weather events),
agents (speak actions become message events). Subscribers: agent comms queues, the WS
broadcaster, the state logger.

**God mode** (`core/godmode.py`): Accepts structured `Event` objects via the API or free-text
NL strings. NL strings are resolved to `Event` objects via a single LLM call using a
constrained tool schema. Events are queued and injected at the start of the next tick before
any agent steps, ensuring agents can respond to them within the same tick.

**Ablation manager** (`core/ablation.py`): A flag registry mapping `(agent_id | None, ModuleFlag)`
to `bool`. Every cognitive module checks its flag before executing; a disabled module returns
its no-op stub result. `agent_id = None` sets a global default for all agents. Flags take
effect at the next tick boundary. Config is JSON-serialisable and versioned in SQLite.

**State logger** (`core/logger.py`): Async writer to SQLite. Writes world snapshots and
the full action log (including raw LLM prompts and responses) every tick. Also maintains a
token ledger for cost tracking.

### 4. Agent Layer

Each agent is a `CivAgent` (subclass of Mesa `Agent`) that owns a cognitive pipeline
assembled at construction time from config. Every pipeline stage implements a `Protocol`
interface defined in `agents/protocols.py`, enabling swap-in of stubs, alternative
implementations, or ablation no-ops without touching the agent or tick engine.

**Perception** (`agents/perception.py`): Reads `WorldSnapshot` for the agent's current
sensory radius (configurable per agent, default 3 tiles Moore neighbourhood). Returns a
structured `Observation`: visible tiles with terrain and resources, nearby agents with
faction and visible state, events received since last tick, own current stats. Ablation
stub returns a minimal self-observation only.

**Memory** (`agents/memory.py`): A `MemoryStream` storing `MemoryEntry` objects with
content string, tick timestamp, importance score (0–1), and an optional embedding vector.
New observations are encoded to entries on each step. Retrieval scores entries by a weighted
sum of recency, importance, and cosine similarity to a query string. Implements the memory
model from Park et al. (Generative Agents, 2023). Ablation stub returns an empty list on
retrieval.

**Reflection** (`agents/reflection.py`): Runs on a configurable interval (default every 5
ticks) rather than every step. Retrieves the highest-importance recent memories and calls
the LLM to synthesise higher-order insights ("what does this tell me about my situation?").
Reflection entries are written back to the memory stream with elevated importance scores.
Ablation stub is a no-op that returns `None`; the planner handles a `None` reflection
gracefully.

**Planner** (`agents/planner.py`): Given the current observation, retrieved memories, and
optional reflection, calls the LLM to produce a `Plan` — a short-horizon goal + ordered
sequence of `Action` intents. The plan is cached in the agent's intention buffer. Re-planning
is triggered when the buffer is empty, a high-importance event crosses the interrupt
threshold, or the re-plan interval fires (configurable, default 3 ticks). Ablation stub
returns a random valid action from the tool registry each tick.

**Tool registry** (`agents/tools/`): A dict of `name → Tool` mappings. Each `Tool`
implements a `call(agent, args, world_snapshot) -> Action` method. The planner outputs tool
name + args; the tick engine resolves these through the registry to concrete `Action`
objects. New tools are added by implementing `ToolProtocol` and registering in
`agents/tools/__init__.py`.

Standard tools: `move`, `harvest`, `consume`, `trade_offer`, `trade_accept`, `speak`,
`build`, `attack`, `rest`, `observe_extended`.

**Identity** (`agents/identity.py`): Immutable agent profile set at spawn. Contains: name,
faction id, trait vector (courage, greed, sociability, aggression — all 0–1 floats),
backstory paragraph, starting skill levels. Identity is serialised into the LLM system
prompt for every call. Not ablatable — it is the generative seed, not a runtime module.

**Comms** (`agents/comms.py`): Inbound message queue populated by the event bus when another
agent's `speak` action targets this agent. Messages are delivered to perception on the next
step as `MessageEvent` entries in the observation. Ablation stub discards all inbound
messages and silently drops outbound speak actions.

### 5. LLM Backends

`llm/base.py` defines the `LLMBackend` protocol:

```python
class LLMBackend(Protocol):
    async def complete(
        self,
        system: str,
        messages: list[Message],
        tools: list[ToolSchema] | None = None,
        max_tokens: int = 1024,
    ) -> LLMResponse: ...
```

Implementations:
- `llm/anthropic_backend.py` — Claude via the `anthropic` async SDK. Supports tool use
  natively for structured planner output. Model and token limits are configurable.
- `llm/openai_backend.py` — OpenAI-compatible endpoint. Works with GPT-4o, local vLLM
  servers, and Ollama. Same tool-use interface via function calling.
- `llm/mock_backend.py` — Returns deterministic scripted responses from a preloaded fixture
  file. Used in testing and during replay (stored responses are replayed verbatim).

Backend is configured per-agent in `SimConfig`. Agents in the same simulation can use
different backends (e.g. Claude for faction leaders, a local model for common agents).

### 6. Persistence

SQLite via `aiosqlite` for non-blocking async writes. Schema in `persistence/schema.sql`,
applied on first run by `persistence/db.py`. All writes go through `persistence/repo.py`
which provides typed async methods and never exposes raw SQL to calling code.

Tables:
- `simulations` — id, name, config JSON, status, seed, created_at, updated_at
- `world_snapshots` — sim_id, tick, snapshot_json, created_at
- `action_log` — sim_id, tick, agent_id, module, prompt, llm_response, action_json, duration_ms
- `events` — sim_id, tick, source, event_type, event_json
- `ablation_configs` — sim_id, version, config_json, applied_at
- `token_ledger` — sim_id, tick, agent_id, backend, input_tokens, output_tokens

---

## Data Flow

### Simulation startup

```
POST /simulations
  → SimConfig validated (Pydantic)
  → WorldGenerator.generate(seed, config.world)     # pynoise terrain + biome + resources
  → CivModel.__init__(generated_world, agents)       # Mesa model constructed
  → SQLite: INSERT simulations                       # persisted immediately
  → return { sim_id, status: "created" }

POST /simulations/{id}/start
  → SimRegistry.get(sim_id)
  → TickEngine.start()                               # spawns asyncio.Task
  → SQLite: UPDATE simulations SET status="running"
  → WS broadcast: { type: "sim_started", tick: 0 }
```

### Per-tick flow

```
TickEngine._run_tick(tick_n):

  1. snapshot = WorldState.snapshot()               # immutable copy for agents this tick
     prev_snapshot = last_snapshot                  # held for rollback and diff

  2. god_events = GodMode.drain_queue()
     EventBus.publish_all(god_events)

  3. actions = await asyncio.wait_for(
       asyncio.gather(*[agent.step(snapshot)
                        for agent in scheduler.agents]),
       timeout=config.tick_timeout_s
     )                                               # all LLM calls run in parallel here

  4. resolved = ActionArbiter.resolve(actions, snapshot)
     for action in resolved.valid:
       CivModel.apply_action(action)                 # synchronous Mesa grid mutations
     EnvLayer.tick()                                 # resource decay + weather
     CivModel.datacollector.collect()

  5. diff = WorldDiff.compute(prev_snapshot, CivModel)
     await StateLogger.write_tick(tick_n, CivModel, actions, resolved)
     await WSBroadcaster.broadcast(tick_n, diff)

  6. tick_n += 1
     await asyncio.sleep(config.tick_interval_s)    # 0 for max speed, >0 for real-time
```

### Agent step (concurrent inside asyncio.gather)

```
CivAgent.step(snapshot: WorldSnapshot) -> Action:

  observation = Perception.observe(snapshot)        # sync, fast, no I/O

  if AblationManager.is_enabled(self.id, MEMORY):
    Memory.add(observation.to_memory_entries())
    memories = Memory.retrieve(observation.context_query, k=20)
  else:
    memories = []

  reflection = None
  if should_reflect(tick_n) and AblationManager.is_enabled(self.id, REFLECTION):
    reflection = await Reflection.run(memories)     # LLM call

  if should_replan(observation) and AblationManager.is_enabled(self.id, PLANNING):
    plan = await Planner.plan(observation, memories, reflection)   # LLM call
    intention_buffer.set(plan)

  action = intention_buffer.next_action()           # from cached plan, no LLM call
  return ToolRegistry.resolve(action)
```

### Replay flow

```
POST /simulations/{id}/replay/seek  { "tick": N }
  → SQLite: SELECT snapshot_json WHERE sim_id=? AND tick=?
  → CivModel.restore(snapshot)                      # Mesa grid rebuilt from JSON
  → ActionLog.load_from(tick=N)                     # stored prompts+responses loaded
  → MockBackend.load_responses(action_log)           # LLM backend swapped to mock
  → TickEngine.resume_from(N)                        # ticks forward using stored responses
  → WS broadcast: { type: "replay_seeked", tick: N }
```

### God mode NL flow

```
POST /simulations/{id}/god  { "command": "cause a drought in the northern region" }
  → LLM call: NL → structured Event (tool schema constrains to valid event types)
  → Event validated: { type: "weather", subtype: "drought", tiles: [...], duration: 10 }
  → GodMode.queue(event)
  → applied at start of next tick, before agent steps
  → EventBus publishes → agents perceive it in that tick's observation
```

---

## Key Abstractions

### `CivModel` (core/model.py)

Mesa `Model` subclass. Owns the grid, agent registry, environment layer, event bus, and
datacollector. Is the single source of truth for world state. Exposes `apply_action(action)`
as the only write path for agent-originated mutations — called exclusively from the
synchronous action resolution pass.

### `WorldSnapshot` (core/world.py)

Immutable, JSON-serialisable snapshot of the full world state at a given tick. Passed to
every agent at step start. Agents never read from the live `CivModel` during their step,
which prevents mid-tick consistency issues and makes the snapshot the unit of persistence.

### `Action` (core/actions.py)

Dataclass union (Python `Union` type with a `kind` discriminator). Every tool produces one:

```
MoveAction(agent_id, target: TileCoord)
HarvestAction(agent_id, resource: ResourceType, tile: TileCoord)
ConsumeAction(agent_id, resource: ResourceType, amount: float)
TradeOfferAction(agent_id, target_agent_id, offer: ResourceBundle, request: ResourceBundle)
TradeAcceptAction(agent_id, offer_id: str)
SpeakAction(agent_id, target_agent_id, content: str)
BuildAction(agent_id, structure: StructureType, tile: TileCoord)
AttackAction(agent_id, target: AgentId | TileCoord)
RestAction(agent_id)
NoOpAction(agent_id, reason: str)
```

### `ActionArbiter` (core/arbiter.py)

Takes the list of all actions from a tick and returns `ArbitrationResult(valid, rejected, deferred)`.
Rules (checked in order): range validation → resource availability → collision resolution →
trade matching → attack priority. All rejections are logged with reason codes.

### `MemoryProtocol` (agents/protocols.py)

```python
class MemoryProtocol(Protocol):
    def add(self, entry: MemoryEntry) -> None: ...
    def retrieve(self, query: str, k: int) -> list[MemoryEntry]: ...
    def score_importance(self, content: str) -> float: ...
    def decay(self) -> None: ...
```

All six cognitive modules are defined as `Protocol` classes in `agents/protocols.py`. This is
the primary extensibility surface for research — new module implementations only need to
satisfy their protocol, and the ablation manager can substitute them at any granularity.

### `AblationManager` (core/ablation.py)

```python
class ModuleFlag(StrEnum):
    PERCEPTION = "perception"
    MEMORY     = "memory"
    REFLECTION = "reflection"
    PLANNING   = "planning"
    COMMS      = "comms"
    TOOLS      = "tools"

class AblationManager:
    def is_enabled(self, agent_id: str | None, module: ModuleFlag) -> bool: ...
    def set_flag(self, agent_id: str | None, module: ModuleFlag, value: bool) -> None: ...
    def snapshot(self) -> AblationConfig: ...
    def restore(self, config: AblationConfig) -> None: ...
```

`agent_id=None` sets a global default. Per-agent flags override globals. Config is
JSON-serialisable and versioned in SQLite.

### `WorldGenerator` (core/worldgen/generator.py)

```python
class WorldGenerator:
    def generate(self, seed: int, config: WorldConfig) -> GeneratedWorld: ...
```

Returns `GeneratedWorld(heightmap, biome_map, resource_map, agent_starts)`. Fully
deterministic from seed + config. The `NoiseStack` inside composes three `pynoise` modules
with configurable octaves, lacunarity, persistence, and scale.

### `LLMBackend` (llm/base.py)

```python
class LLMBackend(Protocol):
    async def complete(
        self,
        system: str,
        messages: list[Message],
        tools: list[ToolSchema] | None = None,
        max_tokens: int = 1024,
    ) -> LLMResponse: ...
```

`LLMResponse` carries `content`, `tool_calls`, `input_tokens`, `output_tokens`, `latency_ms`.
The tick engine never calls this directly — it is called only from within agent pipeline
modules (planner, reflection, god mode NL resolution).

---

## Entry Points

### Application server

```bash
python -m civitas.main [--host 0.0.0.0] [--port 8000] [--log-level info]
```

Starts FastAPI via Uvicorn. Creates `civitas.db` if absent. Registers all routers. Mounts
the built React UI from `ui/dist/` at `/` if the directory exists (production mode). In
development the UI runs on its own Vite dev server and proxies API calls.

### CLI

```bash
civitas run  --config sim.json               # create and immediately start
civitas seed --config sim.json [--seed N]    # generate world preview, write to PNG
civitas bench --ticks 100 --config sim.json  # headless run, output metrics.csv
civitas replay --sim-id abc123 --tick 42     # seek simulation to tick 42
```

### Tests

```bash
pytest tests/unit/           # no LLM calls, no DB
pytest tests/integration/    # mock LLM backend, in-memory SQLite
pytest tests/e2e/            # full stack, requires API keys in env
```

---

## Error Handling

### LLM call failures

All LLM calls go through `llm/retry.py` — async retry with exponential backoff (3 attempts,
base delay 1s, cap 8s). On exhaustion the agent returns its cached intention buffer's next
action. If the buffer is also empty, `NoOpAction` is returned. The failure is written to the
action log with `module = "llm_error"` and the exception message.

A single agent's LLM failure never stalls a tick — `asyncio.gather` always resolves because
the retry wrapper catches all exceptions.

### Tick timeouts

`asyncio.wait_for` wraps the gather with `timeout = config.tick_timeout_s` (default 30s).
Agents whose steps exceed the timeout are cancelled and substituted with `NoOpAction`. The
tick proceeds and the timeout is recorded in the tick metadata.

### World state corruption

The synchronous action resolution pass runs inside a try/except. On unhandled exception the
Mesa model is restored from `prev_snapshot` (held in memory), the simulation is paused, and
the error is written to `simulations.error_log`. The WebSocket broadcasts a `sim_paused`
event with an error reason so the UI can surface it.

### API contract errors

A global FastAPI exception handler maps domain exceptions to HTTP status codes:
- `SimNotFound` → 404
- `SimStateConflict` (e.g. start on running sim) → 409
- Pydantic `ValidationError` → 422
- Unhandled internal errors → 500 with structured error body

### WebSocket disconnection

The broadcaster holds a `set[WebSocket]` per simulation. Disconnects are caught in the send
loop and removed silently. On reconnect, the client sends `{ type: "subscribe", sim_id }` and
receives the full current snapshot before streaming resumes.

---

## Cross-Cutting Concerns

### Seeding and reproducibility

Every simulation carries an integer seed. It is threaded through world generation, Mesa's
internal RNG, action arbiter priority shuffles, and LLM mock backend fixture selection. Given
the same seed, config, and stored LLM responses, a replay run is bit-for-bit identical to the
original. Seed and config are immutable after creation.

### Structured logging

`structlog` throughout. Every event carries `sim_id`, `tick`, and `agent_id` where applicable.
LLM prompts and raw responses are logged at `DEBUG` only. Tick durations and action counts are
logged at `INFO`. The log format is JSON in production and human-readable in development.

### Ablation as a first-class concern

The ablation manager is injected into every `CivAgent` at construction and checked at the
entry point of each module method. It is not bolted on after the fact. Config changes apply
at the next tick boundary and are versioned in SQLite so any experimental configuration is
permanently recoverable.

### LLM cost tracking

Every `LLMResponse` carries `input_tokens` and `output_tokens`. The state logger writes these
to the `token_ledger` table every tick. The `/simulations/{id}/stats` endpoint aggregates
total tokens, estimated cost (configurable rate per backend), and per-agent breakdowns.

### Configuration as code

All simulation parameters are expressed as a Pydantic `SimConfig` model, validated at POST
time and stored as JSON in SQLite. Restarting the process restores all simulations in their
last known state (running sims resume as paused and require an explicit start call). Config
JSON can be exported, version-controlled, and used to reproduce any run.
