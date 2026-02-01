# Bachelor-Projekt: Game-State-Aware SLM for Procedural Quest Generation in Video Games

## Preliminary Problem Statement
### Problem Description: 
Procedurally generating quests in an open-world RPG video game setting, like Skyrim or Shadow of War, generally rely on specific templates or components being matched together. This greatly limits their complexity, makes them repetitive, and they often feel unrelated to the player. Our goal is to see if it is possible to make a Small Language Model (SLM) that can generate quests of greater variety and of more relevance to the player while running on their own machine. The core challenge is to ensure that the generated quests are narratively consistent, respect the giving NPC's role and how it relates to the player, and, most crucially, are mechanically possible within the current game world-state (e.g., targeting existing items, locations, and characters). 

### Project Hypothesis: 
We believe that by leveraging a RAG-enhanced SLM we can generate quests that are completable by the player, while increasing narrative and gameplay variety compared to regular template-based systems. The model will be trained on artificially created game-state data, fabricated quests, and output criteria. While we don’t intend to implement it in a game in this project, we will put some thought into how the output could be formatted to interface with a game.
