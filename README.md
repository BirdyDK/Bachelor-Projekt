# Bachelor-Projekt

## Preliminary Problem Statement
### Problem Description: 
Procedural quest generation in video games often relies on handcrafted templates, thereby limiting dynamism and player-specific adaptation. This project investigates the use of a Small Language Model (SLM) to generate coherent, context-sensitive quests directly from game state data. The core challenge is to ensure that generated quests are narratively consistent, respect the giving NPC's role, and, crucially, are mechanically possible within the current game world state (e.g., targeting existing items, locations, and characters). The project will involve designing a model architecture and prompting/constraining strategy that ingests structured game state (e.g., world facts, NPC roles, player progression) to output executable quest specifications, including lore, objectives, and rewards.
### Project Hypothesis: 
We hypothesize that a small language model, when provided with a structured and constrained representation of the current game world state and narrative context, can generate unique, lore-appropriate, and, most importantly, mechanically feasible quests.