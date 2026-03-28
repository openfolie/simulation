# CLAUDE.md — Simulation

## Project Overview

This is an open-world multi-agent simulation with an effectively infinite world boundary. The goal is to simulate emergent intelligence, survival, reproduction, civilization progression, and scientific discovery through agent interactions with a layered procedural environment.

---

## Architecture

### World Representation

The world is a **2D matrix with multiple stacked layers**. Agents perceive their surroundings via a **Moore neighborhood matrix** (8 surrounding cells + self).

**Layers (bottom to top):**

| Layer | Description |
|---|---|
| Biome | Blended biomes with contour data |
| Wind | Directional wind simulation |
| Water Cycles | Rainfall, rivers, evaporation |
| Geothermal | Volcanic/tectonic events (deferred) |
| Entities | Agents, animals, NPCs |

Biomes have smooth blending at borders (no hard edges). Each biome tile carries a blend weight vector across biome types.

---

## Systems

### Environment

- **Resource patches** distributed across the world tied to biome type (e.g., ore in mountains, food in forests)
- **Climate simulation**: wind + water cycles affect resource availability and traversal cost
- **Non-agentic entities**: animals, NPCs — interact with the world but don't run the full agent intelligence stack

### Survival System

Agents have a survival drive. Two design directions (pick one):

- **Threat-based** (Minecraft-style): hostile entities like zombies create active pressure
- **Baseline scarcity** (life-like): survival pressure comes purely from resource scarcity and environmental difficulty

**Reward function:**
- `+` Survival (staying alive, health, energy)
- `+` Reproduction (passing on genetics)
- Tune weights to balance exploration vs. exploitation vs. cooperation

### Progression System

- **Tech tree / Age system**: agents collectively unlock new capabilities over time
- Progression is tied to accumulated knowledge and discovered actions, not arbitrary gates
- Ages should emerge from agent behavior, not be scripted

---

## Agent Design

### Intelligence

- Agents simulate intelligence through learned action chains and proficiency accumulation
- **Force collaboration**: some tasks must be physically impossible for a single agent — require coordination

### Characteristics (per agent)

- `greed`: tendency to hoard resources
- `envy`: sensitivity to relative resource disparity vs. nearby agents
- Genetic attributes (biome-specific and race-specific trait clusters)

### Growth

Agent capabilities evolve through:
1. **Genetics**: inherited traits from parents
2. **Actions taken during lifetime**: proficiency accumulates

### Action System

- **Base actions** are atomic primitives (move, pick up, attack, craft, communicate, etc.)
- **Chained actions** = composite sequences saved per-agent with a proficiency score
- **Transfer learning**: raising proficiency in one action raises related actions proportionally (muscle memory model)
- Proficiency degrades without practice (optional)

### Genetics System

- Traits are **biome-specific** (cold resistance in tundra agents) and **group-specific**
- No simulating evolution from scratch — genetics are initialized with preset trait distributions and mutate on reproduction
- Reproduction mixes parent trait vectors with noise

> **Note**: We're not running full evolutionary simulation. Genetics provide diversity and heritable identity, not emergent speciation.

---

## Scientific Discovery

Agents should be able to make emergent discoveries. Design directions:

- **Combinatorial action chains**: certain novel action sequences unlock new capabilities when tried for the first time
- **Knowledge graph**: discoveries are nodes; agents share knowledge through proximity/communication
- **Prerequisite gating**: some discoveries only become possible after prior ones are made (mirrors real tech trees)

Keep the discovery mechanism data-driven so new discoveries can be added via config.

---

## Reproducibility

All runs must be fully reproducible:

- **Config format**: YAML or JSON initialization files
- **Mandatory fields**: random seed, world size, biome distribution params, initial agent count, starting age
- **Deterministic RNG**: seed every source of randomness from the config seed

```yaml
# Example init config
seed: 42
world:
  size: [1024, 1024]
  biomes:
    - type: forest
      weight: 0.4
    - type: plains
      weight: 0.35
    - type: tundra
      weight: 0.25
agents:
  initial_count: 100
  trait_variance: 0.2
survival:
  mode: threat  # or: scarcity
progression:
  starting_age: stone
```

---

## Open Questions / Design Decisions

- [ ] **Survival mode**: Zombie-threat vs. pure scarcity — pick one before implementing reward functions
- [ ] **Infinite world**: chunked generation (Minecraft-style) or procedural expansion on demand?
- [ ] **Geothermal layer**: deferred — define the stub interface now so it plugs in cleanly later
- [ ] **Discovery mechanism**: combinatorial chains vs. explicit knowledge graph — impacts agent memory model significantly
- [ ] **Proficiency decay rate**: tune or make configurable per-agent

---

## Implementation Notes

- Keep biome blend logic separate from entity logic — layers should be independently queryable
- Moore matrix perception should be parameterizable (radius = 1 for standard, larger for "scouting" agents)
- Action chain storage per-agent will grow — consider a fixed-size LRU or priority-pruned structure
- Climate simulation tick rate can be decoupled from agent tick rate (run climate every N agent steps)
