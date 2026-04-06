# World-State Based Procedural Quest Generator
The goal is to create a prodecural quest generator that loads a set of world-state data and can then generate a quest for the player character.
This quest should reflect both the NPC giving the quest and the player's former quests. When an NPC belongs to a faction that has a relation level to the player and they have their own relation as well, then they should use the average value of the two. If they don't have a personal relation level, then they just use the faction relation.

The world state data will be given in files formatted like `world_data.csv`.

# Quest Structures and Their Targets.
The quest structure should follow the rules laid out in `reduced_grammar.md`.

## Attack threatening entities
This quest structure should mainly target monsters that can be found in the region. It can be given to the player so long as their relation level to the quest giver of -2 or higher.

## Recover stolen item
This quest structure can be given by NPCs or Factions with a relation of 3 or higher. The target can be any NPC or Faction they dislike.

## Guard entity
This quest structure can be given by Factions with a relation of 2 or higher. The target can be any NPC in the Faction or a friendly Faction.

## Attack enemy
This quest structure can be given by NPCs or Factions with a relation of 1 or higher. The target can be any Faction or NPC they dislike.

## Steal stuff
This quest structure can be given by NPCs or Factions with a relation of 2 or higher. The target can be any Item they desire.

## Kill enemies
This quest structure can only be given by a Faction or NPC with a relation level of 4 or higher, or -4 or lower. This structure is used to kill high-profile targets of oposing Factions or NPCs the quest giver hates, so it's only given to players that the Faction trusts (4 or higher) or to make the player prove that they're willing to go the mile to join them (-4 or lower).