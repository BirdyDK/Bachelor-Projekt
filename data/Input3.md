Now for each of the 20 quests take relavent data for the quest from the game state dataset that could generate that quest and it should be set up like it is in the game state dataset. mutiple quest may have the same data

example:
```
Quest 1: The Poisoned Grove
json
{
  "Quest": {
    "Name": "The Poisoned Grove",
    "Giver": "The Verdant Circle",
    "Actions": ["goto Verdant Vale", "damage Corrupted Treant", "goto The Verdant Circle", "report"]
  },
  "RelevantData": {
    "Factions": {
      "The Verdant Circle": {
        "Name": "The Verdant Circle",
        "Relations": [{"Target": "Player", "Favorability": 3}],
        "Members": ["Eldrin Moonbrook", "Elara Whisperwind", "Doric Ironwood"],
        "FactionLog": [{"Originator": "The Verdant Circle", "Type": "AttackThreateningEntities", "Target": ["Corrupted Treant"], "For": "The Verdant Circle"}]
      }
    },
    "Locations": {
      "Verdant Vale": {
        "Name": "Verdant Vale",
        "Enemies": ["Corrupted Treant", "Forest Spider Matriarch"],
        "Resources": ["Healing Herb", "Iron Ore"]
      }
    },
    "Enemies": {
      "Corrupted Treant": {
        "Name": "Corrupted Treant",
        "Loot": ["Healing Herb", "Iron Ore"]
      }
    }
  }
}
```