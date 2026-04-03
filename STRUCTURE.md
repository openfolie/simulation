# Structure

## Directory Layout

```
civitas/
│
├── main.py                          # Application entry point (Uvicorn startup)
├── cli.py                           # CLI entry point (civitas run / bench / seed)
├── config.py                        # Top-level AppConfig (loaded from env / YAML)
├── pyproject.toml
├── openapi.yaml                     # API contract (source of truth)
│
├── core/                            # Simulation core — Mesa model + tick engine
│   ├── __init__.py
│   ├── model.py                     # CivModel (Mesa Model subclass)
│   ├── engine.py                    # TickEngine — async tick loop
│   ├── arbiter.py                   # ActionArbiter — conflict resolution
│   ├── eventbus.py                  # In-process pub/sub event bus
│   ├── godmode.py                   # God mode — structured + NL event injection
│   ├── ablation.py                  # AblationManager + ModuleFlag enum
│   ├── logger.py                    # StateLogger — async SQLite writes per tick
│   ├── registry.py                  # SimRegistry — in-memory simulation instances
│   ├── scheduler.py                 # AsyncAgentScheduler (replaces Mesa scheduler)
│   ├── world.py                     # WorldSnapshot, WorldDiff, WorldState
│   ├── actions.py                   # Action union type + all Action dataclasses
│   ├── types.py                     # Shared primitives: TileCoord, AgentId, Tick, etc.
│   │
│   ├── env/                         # Environment layer — dynamic world state
│   │   ├── __init__.py
│   │   ├── layer.py                 # EnvLayer — top-level resource + weather controller
│   │   ├── resources.py             # ResourceNode, ResourceType, regeneration logic
│   │   ├── weather.py               # WeatherSystem — probabilistic weather events
│   │   ├── biomes.py                # BiomeType enum + biome property tables
│   │   └── reader.py                # EnvReader — read-only view for agent perception
│   │
│   └── worldgen/                    # Procedural world generation
│       ├── __init__.py
│       ├── generator.py             # WorldGenerator — top-level orchestrator
│       ├── noise.py                 # NoiseStack — pynoise composition (Perlin + Ridged + Billow)
│       ├── heightmap.py             # HeightmapBuilder — terrain from noise
│       ├── moisture.py              # MoisturePass — independent moisture noise layer
│       ├── biome_map.py             # BiomeMapper — (height, moisture) → BiomeType
│       ├── resource_placer.py       # ResourcePlacer — biome-aware resource seeding
│       ├── agent_placer.py          # AgentPlacer — starting position assignment
│       └── schema.py                # WorldConfig, GeneratedWorld dataclasses
│
├── agents/                          # Agent cognitive pipeline
│   ├── __init__.py
│   ├── base.py                      # CivAgent (Mesa Agent subclass) — pipeline owner
│   ├── protocols.py                 # Protocol interfaces for all 6 pipeline modules
│   ├── identity.py                  # IdentityProfile — immutable agent seed
│   ├── perception.py                # PerceptionModule — WorldSnapshot → Observation
│   ├── memory.py                    # MemoryStream, MemoryEntry, importance scoring
│   ├── reflection.py                # ReflectionModule — periodic LLM synthesis
│   ├── planner.py                   # PlannerModule — LLM → Plan + intention buffer
│   ├── comms.py                     # CommsModule — inbound message queue
│   ├── observation.py               # Observation dataclass + serialisation helpers
│   ├── plan.py                      # Plan, PlanStep, IntentionBuffer dataclasses
│   ├── stubs.py                     # Ablation no-op stubs for every protocol
│   │
│   └── tools/                       # Tool registry — pluggable agent actions
│       ├── __init__.py              # ToolRegistry, register() decorator
│       ├── base.py                  # ToolProtocol, ToolSchema, ToolResult
│       ├── move.py                  # MoveAction
│       ├── harvest.py               # HarvestAction
│       ├── consume.py               # ConsumeAction
│       ├── trade.py                 # TradeOfferAction, TradeAcceptAction
│       ├── speak.py                 # SpeakAction
│       ├── build.py                 # BuildAction
│       ├── attack.py                # AttackAction
│       ├── rest.py                  # RestAction
│       └── observe.py               # ObserveExtendedAction
│
├── llm/                             # LLM backend abstraction layer
│   ├── __init__.py
│   ├── base.py                      # LLMBackend Protocol, Message, LLMResponse
│   ├── retry.py                     # Async retry decorator with exponential backoff
│   ├── anthropic_backend.py         # Claude via anthropic SDK
│   ├── openai_backend.py            # OpenAI-compatible (GPT / vLLM / Ollama)
│   └── mock_backend.py              # Deterministic fixture-based backend (tests + replay)
│
├── api/                             # FastAPI application
│   ├── __init__.py
│   ├── app.py                       # FastAPI app factory, middleware, global handlers
│   ├── deps.py                      # Dependency injection (SimRegistry, DB session)
│   ├── models.py                    # Pydantic request/response schemas (API contract)
│   │
│   ├── router/                      # REST routers (one file per resource)
│   │   ├── __init__.py
│   │   ├── sim.py                   # /simulations CRUD + lifecycle
│   │   ├── world.py                 # /simulations/{id}/world
│   │   ├── agents.py                # /simulations/{id}/agents
│   │   ├── events.py                # /simulations/{id}/events + /god
│   │   ├── ablation.py              # /simulations/{id}/ablation
│   │   ├── replay.py                # /simulations/{id}/replay
│   │   └── stats.py                 # /simulations/{id}/stats
│   │
│   └── ws/                          # WebSocket handlers
│       ├── __init__.py
│       ├── tick.py                  # /ws/{sim_id}/tick — tick-diff stream
│       └── broadcaster.py           # WSBroadcaster — fan-out to all subscribers
│
├── persistence/                     # SQLite persistence layer
│   ├── __init__.py
│   ├── db.py                        # Connection pool, schema migration on startup
│   ├── schema.sql                   # DDL — all CREATE TABLE statements
│   ├── repo.py                      # SimRepository — typed async CRUD methods
│   └── serialisers.py               # WorldSnapshot ↔ JSON, Action ↔ JSON helpers
│
├── schemas/                         # Shared data contracts (cross-layer)
│   ├── __init__.py
│   ├── sim_config.py                # SimConfig (Pydantic) — full simulation spec
│   ├── world_config.py              # WorldConfig — terrain + biome generation params
│   ├── agent_config.py              # AgentConfig — per-agent pipeline + LLM config
│   └── ablation_config.py           # AblationConfig — full flag set, JSON-serialisable
│
├── tests/
│   ├── conftest.py                  # Shared fixtures (mock LLM, in-memory DB, test world)
│   ├── unit/
│   │   ├── test_worldgen.py         # Terrain generation determinism and biome coverage
│   │   ├── test_arbiter.py          # Action conflict resolution cases
│   │   ├── test_memory.py           # Memory retrieval scoring
│   │   ├── test_ablation.py         # Flag resolution and stub substitution
│   │   ├── test_actions.py          # Action serialisation round-trips
│   │   └── test_env.py              # Resource decay and weather application
│   ├── integration/
│   │   ├── test_tick_engine.py      # Full tick with mock LLM, in-memory DB
│   │   ├── test_agent_pipeline.py   # Perception → memory → plan pipeline
│   │   ├── test_godmode.py          # NL → event resolution
│   │   ├── test_replay.py           # Snapshot seek + mock backend replay
│   │   └── test_api.py              # FastAPI test client against all routers
│   └── e2e/
│       └── test_full_run.py         # 10-tick run with real LLM backend
│
└── ui/                              # React + Vite frontend
    ├── index.html
    ├── vite.config.ts
    ├── package.json
    ├── tsconfig.json
    ├── src/
    │   ├── main.tsx                 # React entry point
    │   ├── App.tsx                  # Root layout, routing
    │   │
    │   ├── api/                     # API client layer
    │   │   ├── client.ts            # Axios instance + base URL config
    │   │   ├── simulations.ts       # Simulation lifecycle calls
    │   │   ├── world.ts             # World state fetches
    │   │   ├── agents.ts            # Agent detail fetches
    │   │   ├── events.ts            # Event injection + god mode
    │   │   └── replay.ts            # Replay control
    │   │
    │   ├── ws/                      # WebSocket client
    │   │   ├── tickStream.ts        # WS connection + tick-diff handler
    │   │   └── useTickStream.ts     # React hook wrapping tickStream
    │   │
    │   ├── store/                   # Zustand global state
    │   │   ├── simStore.ts          # Active simulation + status
    │   │   ├── worldStore.ts        # Live world state + diff application
    │   │   ├── agentStore.ts        # Selected agent + inspector state
    │   │   └── uiStore.ts           # Overlay mode, panel visibility, speed
    │   │
    │   ├── components/
    │   │   ├── WorldViewport/       # Canvas tile grid renderer + overlays
    │   │   │   ├── WorldViewport.tsx
    │   │   │   ├── TileRenderer.ts  # Canvas drawing primitives
    │   │   │   ├── OverlayLayer.ts  # Faction / resource / health overlays
    │   │   │   └── AgentSprite.ts   # Agent position + state icons
    │   │   ├── AgentInspector/      # Agent detail panel
    │   │   │   ├── AgentInspector.tsx
    │   │   │   ├── MemoryList.tsx
    │   │   │   ├── PlanTree.tsx
    │   │   │   └── LLMCallLog.tsx
    │   │   ├── GodControls/         # Event injection panel
    │   │   │   ├── GodControls.tsx
    │   │   │   ├── NLCommandBar.tsx
    │   │   │   └── EventPalette.tsx
    │   │   ├── ExperimentPanel/     # Ablation config UI
    │   │   │   ├── ExperimentPanel.tsx
    │   │   │   ├── AblationMatrix.tsx
    │   │   │   └── ConfigExport.tsx
    │   │   └── Timeline/            # Scrubber + playback controls
    │   │       ├── Timeline.tsx
    │   │       └── SpeedControl.tsx
    │   │
    │   └── types/                   # TypeScript types mirroring API models
    │       ├── simulation.ts
    │       ├── world.ts
    │       ├── agent.ts
    │       └── events.ts
    └── dist/                        # Built output (gitignored, served by FastAPI in prod)
```

---

## Directory Purposes

| Directory | Owns | Does not own |
|---|---|---|
| `core/` | World state, tick loop, action resolution, persistence writes | Agent cognition, LLM calls |
| `core/env/` | Dynamic resource and weather state | Terrain/biome data (static after worldgen) |
| `core/worldgen/` | Procedural generation from seed | Ongoing simulation state |
| `agents/` | Cognitive pipeline, memory, planning | World mutation (write via Action return only) |
| `agents/tools/` | Mapping from tool name+args to Action objects | Executing actions against world |
| `llm/` | HTTP calls to LLM APIs, retry logic | Prompt construction (done in pipeline modules) |
| `api/` | HTTP surface, request validation, WebSocket fan-out | Business logic |
| `api/router/` | Route handlers, response shaping | State — reads via deps.py injected services |
| `persistence/` | SQLite schema, typed queries | Simulation logic |
| `schemas/` | Shared Pydantic models used across layers | Layer-specific logic |
| `tests/` | Test fixtures and cases | Production code |
| `ui/` | Frontend display and interaction | Backend logic |

---

## Key File Locations

| Concern | File |
|---|---|
| Start the server | `main.py` |
| FastAPI app factory | `api/app.py` |
| All API route definitions | `api/router/*.py` |
| OpenAPI contract | `openapi.yaml` |
| Pydantic API schemas | `api/models.py` |
| Simulation config schema | `schemas/sim_config.py` |
| Mesa model | `core/model.py` |
| Async tick loop | `core/engine.py` |
| Action types | `core/actions.py` |
| Action conflict resolution | `core/arbiter.py` |
| Ablation flags | `core/ablation.py` |
| Noise / terrain generation | `core/worldgen/noise.py`, `core/worldgen/heightmap.py` |
| Biome assignment | `core/worldgen/biome_map.py` |
| Resource seeding | `core/worldgen/resource_placer.py` |
| Dynamic resource state | `core/env/resources.py` |
| Weather system | `core/env/weather.py` |
| Agent base class | `agents/base.py` |
| All module protocols | `agents/protocols.py` |
| All ablation stubs | `agents/stubs.py` |
| Memory implementation | `agents/memory.py` |
| Planner | `agents/planner.py` |
| Tool registry | `agents/tools/__init__.py` |
| Adding a new tool | `agents/tools/<name>.py` + register in `agents/tools/__init__.py` |
| LLM backend interface | `llm/base.py` |
| Claude backend | `llm/anthropic_backend.py` |
| Mock backend (tests) | `llm/mock_backend.py` |
| SQLite schema | `persistence/schema.sql` |
| All DB queries | `persistence/repo.py` |
| WebSocket broadcaster | `api/ws/broadcaster.py` |
| World canvas rendering | `ui/src/components/WorldViewport/TileRenderer.ts` |
| Global UI state | `ui/src/store/worldStore.ts` |

---

## Naming Conventions

### Python

| Thing | Convention | Example |
|---|---|---|
| Modules / packages | `snake_case` | `tick_engine.py`, `biome_map.py` |
| Classes | `PascalCase` | `CivAgent`, `MemoryStream`, `WorldSnapshot` |
| Protocol classes | `PascalCase` + `Protocol` suffix | `MemoryProtocol`, `LLMBackend` |
| Dataclasses | `PascalCase` | `MemoryEntry`, `TileCoord`, `LLMResponse` |
| Enums | `PascalCase` + descriptive suffix | `ModuleFlag`, `BiomeType`, `ResourceType` |
| Functions / methods | `snake_case` | `resolve_conflicts()`, `to_memory_entries()` |
| Async functions | `snake_case` with `async def`, no extra prefix | `async def complete(...)` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_TICK_TIMEOUT`, `MAX_MEMORY_ENTRIES` |
| Private helpers | `_leading_underscore` | `_run_tick()`, `_score_entry()` |
| Type aliases | `PascalCase` | `AgentId = str`, `Tick = int` |
| Test files | `test_<module>.py` | `test_arbiter.py` |
| Test functions | `test_<what_and_condition>` | `test_move_collision_lower_priority_deferred` |

### TypeScript / React

| Thing | Convention | Example |
|---|---|---|
| Component files | `PascalCase.tsx` | `AgentInspector.tsx` |
| Hook files | `useCamelCase.ts` | `useTickStream.ts` |
| Store files | `camelCaseStore.ts` | `worldStore.ts` |
| Utility files | `camelCase.ts` | `tileRenderer.ts` |
| Type files | `camelCase.ts` | `agent.ts` |
| Component directories | `PascalCase/` | `WorldViewport/` |
| Zustand stores | named export, `use` prefix | `export const useWorldStore` |

### Files and directories

- One class per file for major domain objects (`CivAgent`, `MemoryStream`, `TickEngine`)
- Group small related dataclasses in a single file (`core/actions.py`, `core/types.py`)
- `__init__.py` files export the public surface of a package; internal helpers are not
  re-exported
- Test file names mirror the module they test (`core/arbiter.py` → `tests/unit/test_arbiter.py`)

---

## File Organisation Principles

**Dependency direction is strictly downward.** `core/` may not import from `agents/` or
`api/`. `agents/` may not import from `core/engine.py` or `api/`. The dependency graph is:

```
ui → api → core → agents → llm
              ↓
          persistence
              ↓
           schemas  (shared, no upward imports)
```

`schemas/` is the only package imported freely by all layers. It contains only Pydantic
models and enums — no logic.

**Protocols live at the boundary.** `agents/protocols.py` defines what the core engine
expects from agents. `llm/base.py` defines what agent modules expect from LLM backends.
Neither file imports from the other side of the boundary.

**Stubs are co-located with protocols.** `agents/stubs.py` implements every ablation no-op
in one place so they are easy to audit. Stubs import from `agents/protocols.py` only.

**Configuration is always Pydantic.** Every configurable surface (simulation, world gen,
agent, ablation) is a Pydantic model in `schemas/`. This provides validation, JSON
round-tripping, and IDE autocomplete everywhere.

**No business logic in routers.** Router handlers do three things: validate the request,
call a service (via injected dep), return a response. All logic lives in `core/` or `agents/`.

**World mutation is a single path.** The only way to change world state is:
1. `CivModel.apply_action(action)` inside the synchronous resolution pass in `engine.py`
2. `EnvLayer.tick()` in `engine.py`
3. God mode events, applied via the same `apply_action` path

There is no other write path. Agent modules return `Action` objects — they never hold a
reference to `CivModel`.

---

## Where to Add New Code

### New agent tool

1. Create `agents/tools/<name>.py` implementing `ToolProtocol`
2. Define the corresponding `Action` dataclass in `core/actions.py`
3. Add arbitration logic for the action type in `core/arbiter.py`
4. Add the world mutation logic to `core/model.py → apply_action()`
5. Register the tool in `agents/tools/__init__.py`
6. Add unit tests in `tests/unit/test_actions.py` and `tests/unit/test_arbiter.py`

### New cognitive module

1. Add the `Protocol` definition to `agents/protocols.py`
2. Create the implementation in `agents/<module_name>.py`
3. Add the ablation stub to `agents/stubs.py`
4. Add the `ModuleFlag` value to `core/ablation.py`
5. Wire the module into `CivAgent.__init__` in `agents/base.py` (respecting ablation flag)
6. Add unit tests in `tests/unit/test_<module_name>.py`

### New world generation feature

1. Add the generation logic as a new module under `core/worldgen/`
2. Add any new config fields to `schemas/world_config.py`
3. Wire it into `WorldGenerator.generate()` in `core/worldgen/generator.py`
4. Add determinism tests in `tests/unit/test_worldgen.py`

### New API endpoint

1. Add the Pydantic request/response models to `api/models.py`
2. Add the route handler to the appropriate `api/router/<resource>.py`
3. Register the router in `api/app.py` if it is a new file
4. Update `openapi.yaml` to reflect the new endpoint
5. Add tests in `tests/integration/test_api.py`

### New LLM backend

1. Create `llm/<provider>_backend.py` implementing `LLMBackend` from `llm/base.py`
2. Add the backend name to the `LLMBackendType` enum in `schemas/agent_config.py`
3. Add instantiation logic to the backend factory in `llm/__init__.py`
4. Add mock fixtures for the backend in `tests/conftest.py`

### New environment rule

1. Add the rule logic to `core/env/layer.py → EnvLayer.tick()`
2. If the rule needs new state, add fields to `core/env/resources.py` or a new module
3. Expose relevant state through `core/env/reader.py` so agents can perceive it
4. Add unit tests in `tests/unit/test_env.py`

---

## Special Directories

### `core/worldgen/`

The only place where `pynoise` is imported. All procedural generation is isolated here.
Nothing outside this package should construct noise generators — callers use
`WorldGenerator.generate()` and receive a `GeneratedWorld` dataclass. The package has no
dependencies on Mesa; it is pure data transformation from seed + config to map data.

### `agents/tools/`

The plug-in surface for agent capabilities. Every file in this directory (except `base.py`
and `__init__.py`) is one tool. The `register()` decorator in `__init__.py` adds the tool to
the global `ToolRegistry` automatically on import. The `ToolRegistry` is a module-level
singleton — it is never re-instantiated. Tools are stateless; all state lives on the agent
or in the world snapshot passed to `call()`.

### `agents/stubs.py`

A single file containing all six ablation stubs. Keeping them together makes it easy to
verify that every stub returns a type-correct empty result without running LLM calls or
reading world state. Any method on a stub that would require I/O raises `StubNotCallable`
in test mode so accidental stub use surfaces immediately.

### `persistence/`

The only package that imports `aiosqlite`. All other packages access the database exclusively
through `persistence/repo.py`. Raw SQL never appears outside `repo.py` and `schema.sql`. The
`db.py` module manages the connection pool and runs schema migrations on startup using a
simple version table — no external migration tool required.

### `schemas/`

Imported by every layer. Has zero imports from `core/`, `agents/`, `api/`, `llm/`, or
`persistence/`. If a Pydantic model needs to import from one of those packages, it belongs
in that package's local module, not in `schemas/`. This constraint keeps `schemas/` as a
dependency-free shared vocabulary.

### `tests/conftest.py`

Defines shared pytest fixtures used across unit and integration tests:
- `mock_llm` — `MockBackend` instance with a default fixture file
- `test_db` — in-memory SQLite with the full schema applied
- `small_world` — 10×10 generated world, seed=42
- `test_sim` — a fully constructed `CivModel` with 3 agents using mock LLM
- `api_client` — FastAPI `TestClient` with injected mock dependencies

Fixtures are scoped appropriately: `small_world` and `mock_llm` are `session`-scoped
(expensive to construct), `test_sim` and `api_client` are `function`-scoped (mutated by tests).
