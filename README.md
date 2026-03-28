# Simulation

## Overview
- Openworld environment
- Infinite limit world
- Spawn agents

## Environment Design
- Environment should enable gathering resources
- Resource patches in the world like terrains and biomes
- Animals, NPCs, non-agentic entities
- Climate simulation

## Progression System
- Concept of ages / progression (tech tree)

## Survival System
- Incentive to survive
  - Decide between zombies like Minecraft or a basic world like life

### Reward Function
- Survival
- Reproduction

## Agent Intelligence
- Simulate intelligence
- Force collaboration

## Agent Characteristics
- Greed
- Envy
- Genetic attributes

## Agent Growth
- Growth of agents through genetics and actions they take as they grow

## Scientific Discovery
- How do we enable them to make scientific discoveries?

## Actions System
- Base actions that will be linked together

### Implementation Approach
- Muscle memory implementation (practice makes perfect)
- Chained actions will be saved to every agent with a proficiency score
- Similar tasks will raise other similar tasks' proficiency scores

## Genetics System
- Genetics will have biome-specific traits and other race-specific traits (racism)
- Cannot simulate genetics properly since we are not simulating evolution from scratch

## Reproducibility
- Use YAML or JSON files with initialization configs and random seeds

## World Representation
- Moore matrix for agents
- 2D matrix with layers

### Layers
- Biome (biome blend with contours)
- Wind, water cycles
- Geothermal events (later)
