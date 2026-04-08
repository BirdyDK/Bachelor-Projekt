<!--this one with the example does not seem to work it keeps making the same output--> 
You are a video game developer with 15 years of experience. You have to make a full set of game state data that's written in a markdown and json format following this logic:
md
## ENUM DATA
//enum data here

;## GAME STATE DATA
### NPC DATA
NPC1 NAME: //json here
NPC2 NAME: //json here

### FACTION DATA
FACTION1 NAME: //json here
FACTION1 NAME: //json here

### ENEMY DATA
ENEMY1 NAME: //json here 
ENEMY2 NAME: //json here 
;## PLAYER DATA
//json here
## Content 
It should readable by a csv linter that separates on ';'. There should be more than: - 10 NPCs - 10 Items - 4 Locations - 3 Factions - 5 Enemies - 10 Logs for the player, with at least 3 being previously completed quests ## Relations and Logs All logs should relate to the player, whether it's the player completing a quest or killing an NPC or a Faction's member. # Rules spec ## Enums There are two categories of enums used. The first is the "Types" category, which is just all available types of the prefix. The second is essentially a list of all the available options for that object. An example would be that NPCs has the names of all NPCs. This is to avoid having looping references in the other objects. ### Types - ItemTypes - QuestTypes (AttackThreateningEntities, RecoverStolenItem, GuardEntity, AttackEnemy, StealStuff, KillEnemies) - EventTypes - RelationshipLevels (Each level needs a name with Sworn Enemy at -5 and Sworn Ally at +5) ### Lists - Species - Roles - Locations - Factions - Locations - Factions - Enemies - Items - NPCs - Player (only has one value) ## Player Species : Species FactionRelations : list[Relation] NPCRelations : list[Relation] PartyMembers : list[NPCs] Inventory : dict[Items, int] (the items and amount of them) PlayerLog : list[Log] Location : Locations Skills : list[Skill] ## NPC Name : string Species : Species HomeLocation : Locations CurrentLocation : Locations Faction : Factions OwnedItems : dict[Items, int] (the items and amount of them) Role : Roles Relations : list [Relation] NPCLog : list[Log] ## Location Name : string Enemies : list[Enemies] Resources : list[Items] ## Relation Target : Factions | NPCs | Player Favorability : RelationshipLevels ## Faction Name : string Relations : list[Relation] Members : list[NPCs] Treasury : dict[Items, int] (the items and amount of them) FactionLog : list[Log] ## Skill Name : string Level : int ## Enemy Name : string Loot : list[Items] ## Log Originator : Player | NPCs | Factions | Enemies Type : QuestTypes | EventTypes Target : list[Player | NPCs | Factions | Items | Enemies] (This is who's targeted by the quest or event, e.g. the person to be killed) For : Player | NPCs | Factions (This is who takes on the quest or event, e.g. the Player) Received : dict[Items, int] (the items and amount of them) | None Favorability : int

example
```
## ENUM DATA
{
  "Types": {
    "ItemTypes": ["Weapon", "Armor", "Potion", "Ingredient", "Key", "Artifact", "Currency"],
    "QuestTypes": ["AttackThreateningEntities", "RecoverStolenItem", "GuardEntity", "AttackEnemy", "StealStuff", "KillEnemies"],
    "EventTypes": ["Ambush", "Discovery", "Betrayal", "Alliance", "TradeRouteOpened", "ResourceDepleted"],
    "RelationshipLevels": {"-5": "Sworn Enemy", "-4": "Bitter Rival", "-3": "Hated", "-2": "Disliked", "-1": "Annoyed", "0": "Neutral", "1": "Acquainted", "2": "Friendly", "3": "Trusted", "4": "Close Ally", "5": "Sworn Ally"}
  },
  "Lists": {
    "Species": ["Human", "Elf", "Dwarf", "Orc", "Halfling", "Lizardfolk"],
    "Roles": ["Innkeeper", "Blacksmith", "Merchant", "GuardCaptain", "Apothecary", "Thief", "Wizard", "Ranger", "Bard", "Priest"],
    "Locations": ["Whispering Pines Inn", "The Rusty Anvil", "Murkwood Forest", "Shadowfen Marsh", "Sunstone Keep", "Glimmerdale", "Northwatch Tower", "Crimson Creek"],
    "Factions": ["The Iron Covenant", "The Verdant Circle", "The Ashen Claw", "Sunspear Militia"],
    "Enemies": ["Forest Goblin", "Marsh Troll", "Cultist Fanatic", "Iron Covenant Raider", "Shadow Viper", "Corrupted Treant"],
    "Items": ["Iron Sword", "Leather Vest", "Health Potion", "Mana Potion", "Iron Shield", "Silver Key", "Mysterious Herb", "Dwarven Ale", "Healing Poultice", "Lockpick Set", "Obsidian Arrowhead", "Scroll of Fireball", "Steel Gauntlets", "Elven Bread"],
    "NPCs": ["Elara Nightshade", "Borin Ironfoot", "Lyra Swiftarrow", "Grimgar the Old", "Mira Thornwood", "Aldric the Wise", "Sera Goldleaf", "Torvin Stonehand", "Faelan Moonshadow", "Greta Honeywell", "Marcus Vane"],
    "Player": ["Kaelen"]
  }
}
;
## GAME STATE DATA
### NPC DATA
Elara Nightshade: {
  "Name": "Elara Nightshade",
  "Species": "Elf",
  "HomeLocation": "Whispering Pines Inn",
  "CurrentLocation": "Whispering Pines Inn",
  "Faction": "The Verdant Circle",
  "OwnedItems": {
    "Mysterious Herb": 3,
    "Healing Poultice": 2
  },
  "Role": "Apothecary",
  "Relations": [
    {"Target": "Kaelen", "Favorability": 2},
    {"Target": "The Iron Covenant", "Favorability": -2}
  ],
  "NPCLog": []
}

Borin Ironfoot: {
  "Name": "Borin Ironfoot",
  "Species": "Dwarf",
  "HomeLocation": "The Rusty Anvil",
  "CurrentLocation": "The Rusty Anvil",
  "Faction": "The Iron Covenant",
  "OwnedItems": {
    "Iron Sword": 1,
    "Steel Gauntlets": 1
  },
  "Role": "Blacksmith",
  "Relations": [
    {"Target": "Kaelen", "Favorability": 1},
    {"Target": "The Verdant Circle", "Favorability": -1}
  ],
  "NPCLog": []
}

Lyra Swiftarrow: {
  "Name": "Lyra Swiftarrow",
  "Species": "Elf",
  "HomeLocation": "Glimmerdale",
  "CurrentLocation": "Murkwood Forest",
  "Faction": "The Verdant Circle",
  "OwnedItems": {},
  "Role": "Ranger",
  "Relations": [
    {"Target": "Kaelen", "Favorability": 3}
  ],
  "NPCLog": []
}

Grimgar the Old: {
  "Name": "Grimgar the Old",
  "Species": "Human",
  "HomeLocation": "Northwatch Tower",
  "CurrentLocation": "Northwatch Tower",
  "Faction": "Sunspear Militia",
  "OwnedItems": {
    "Scroll of Fireball": 1
  },
  "Role": "Wizard",
  "Relations": [
    {"Target": "Kaelen", "Favorability": 2},
    {"Target": "The Ashen Claw", "Favorability": -3}
  ],
  "NPCLog": []
}

Mira Thornwood: {
  "Name": "Mira Thornwood",
  "Species": "Human",
  "HomeLocation": "Whispering Pines Inn",
  "CurrentLocation": "Whispering Pines Inn",
  "Faction": null,
  "OwnedItems": {
    "Dwarven Ale": 5,
    "Elven Bread": 3
  },
  "Role": "Innkeeper",
  "Relations": [
    {"Target": "Kaelen", "Favorability": 4}
  ],
  "NPCLog": []
}

Aldric the Wise: {
  "Name": "Aldric the Wise",
  "Species": "Human",
  "HomeLocation": "Sunstone Keep",
  "CurrentLocation": "Sunstone Keep",
  "Faction": "Sunspear Militia",
  "OwnedItems": {},
  "Role": "GuardCaptain",
  "Relations": [
    {"Target": "Kaelen", "Favorability": 1},
    {"Target": "The Ashen Claw", "Favorability": -4}
  ],
  "NPCLog": []
}

Sera Goldleaf: {
  "Name": "Sera Goldleaf",
  "Species": "Halfling",
  "HomeLocation": "Glimmerdale",
  "CurrentLocation": "Glimmerdale",
  "Faction": null,
  "OwnedItems": {
    "Lockpick Set": 1,
    "Silver Key": 1
  },
  "Role": "Merchant",
  "Relations": [
    {"Target": "Kaelen", "Favorability": 0}
  ],
  "NPCLog": []
}

Torvin Stonehand: {
  "Name": "Torvin Stonehand",
  "Species": "Dwarf",
  "HomeLocation": "The Rusty Anvil",
  "CurrentLocation": "The Rusty Anvil",
  "Faction": "The Iron Covenant",
  "OwnedItems": {
    "Iron Shield": 2
  },
  "Role": "Blacksmith",
  "Relations": [
    {"Target": "Kaelen", "Favorability": 0}
  ],
  "NPCLog": []
}

Faelan Moonshadow: {
  "Name": "Faelan Moonshadow",
  "Species": "Elf",
  "HomeLocation": "Glimmerdale",
  "CurrentLocation": "Shadowfen Marsh",
  "Faction": "The Verdant Circle",
  "OwnedItems": {
    "Obsidian Arrowhead": 4
  },
  "Role": "Ranger",
  "Relations": [
    {"Target": "Kaelen", "Favorability": 2},
    {"Target": "The Ashen Claw", "Favorability": -1}
  ],
  "NPCLog": []
}

Greta Honeywell: {
  "Name": "Greta Honeywell",
  "Species": "Human",
  "HomeLocation": "Whispering Pines Inn",
  "CurrentLocation": "Whispering Pines Inn",
  "Faction": null,
  "OwnedItems": {},
  "Role": "Bard",
  "Relations": [
    {"Target": "Kaelen", "Favorability": 1}
  ],
  "NPCLog": []
}
;
### FACTION DATA
The Iron Covenant: {
  "Name": "The Iron Covenant",
  "Relations": [
    {"Target": "The Verdant Circle", "Favorability": -3},
    {"Target": "Sunspear Militia", "Favorability": -2},
    {"Target": "Kaelen", "Favorability": -1}
  ],
  "Members": ["Borin Ironfoot", "Torvin Stonehand"],
  "Treasury": {
    "Iron Sword": 5,
    "Iron Shield": 4
  },
  "FactionLog": []
}

The Verdant Circle: {
  "Name": "The Verdant Circle",
  "Relations": [
    {"Target": "The Iron Covenant", "Favorability": -4},
    {"Target": "The Ashen Claw", "Favorability": -2},
    {"Target": "Kaelen", "Favorability": 3}
  ],
  "Members": ["Elara Nightshade", "Lyra Swiftarrow", "Faelan Moonshadow"],
  "Treasury": {
    "Mysterious Herb": 10,
    "Healing Poultice": 5
  },
  "FactionLog": []
}

The Ashen Claw: {
  "Name": "The Ashen Claw",
  "Relations": [
    {"Target": "The Verdant Circle", "Favorability": -3},
    {"Target": "Sunspear Militia", "Favorability": -5},
    {"Target": "Kaelen", "Favorability": -2}
  ],
  "Members": [],
  "Treasury": {},
  "FactionLog": []
}
;
### ENEMY DATA
Forest Goblin: {
  "Name": "Forest Goblin",
  "Loot": ["Iron Sword", "Health Potion"]
}

Marsh Troll: {
  "Name": "Marsh Troll",
  "Loot": ["Mysterious Herb", "Healing Poultice"]
}

Cultist Fanatic: {
  "Name": "Cultist Fanatic",
  "Loot": ["Scroll of Fireball", "Silver Key"]
}

Iron Covenant Raider: {
  "Name": "Iron Covenant Raider",
  "Loot": ["Iron Sword", "Iron Shield"]
}

Shadow Viper: {
  "Name": "Shadow Viper",
  "Loot": ["Obsidian Arrowhead"]
}

Corrupted Treant: {
  "Name": "Corrupted Treant",
  "Loot": ["Elven Bread", "Mysterious Herb"]
}
;
### LOCATION DATA
Whispering Pines Inn: {
  "Name": "Whispering Pines Inn",
  "Enemies": [],
  "Resources": ["Dwarven Ale", "Elven Bread"]
}

The Rusty Anvil: {
  "Name": "The Rusty Anvil",
  "Enemies": [],
  "Resources": ["Iron Sword", "Iron Shield", "Steel Gauntlets"]
}

Murkwood Forest: {
  "Name": "Murkwood Forest",
  "Enemies": ["Forest Goblin", "Corrupted Treant"],
  "Resources": ["Mysterious Herb", "Elven Bread"]
}

Shadowfen Marsh: {
  "Name": "Shadowfen Marsh",
  "Enemies": ["Marsh Troll", "Shadow Viper"],
  "Resources": ["Healing Poultice"]
}

Sunstone Keep: {
  "Name": "Sunstone Keep",
  "Enemies": [],
  "Resources": ["Lockpick Set"]
}
;
### ITEM DATA
Iron Sword: { "Type": "Weapon" }
Leather Vest: { "Type": "Armor" }
Health Potion: { "Type": "Potion" }
Mana Potion: { "Type": "Potion" }
Iron Shield: { "Type": "Armor" }
Silver Key: { "Type": "Key" }
Mysterious Herb: { "Type": "Ingredient" }
Dwarven Ale: { "Type": "Item" }
Healing Poultice: { "Type": "Potion" }
Lockpick Set: { "Type": "Tool" }
Obsidian Arrowhead: { "Type": "Item" }
Scroll of Fireball: { "Type": "Item" }
Steel Gauntlets: { "Type": "Armor" }
Elven Bread: { "Type": "Item" }
;
## PLAYER DATA
{
  "Species": "Human",
  "FactionRelations": [
    {"Target": "The Iron Covenant", "Favorability": -1},
    {"Target": "The Verdant Circle", "Favorability": 3},
    {"Target": "The Ashen Claw", "Favorability": -2}
  ],
  "NPCRelations": [
    {"Target": "Elara Nightshade", "Favorability": 2},
    {"Target": "Mira Thornwood", "Favorability": 4},
    {"Target": "Lyra Swiftarrow", "Favorability": 3},
    {"Target": "Grimgar the Old", "Favorability": 2}
  ],
  "PartyMembers": ["Lyra Swiftarrow"],
  "Inventory": {
    "Health Potion": 3,
    "Iron Sword": 1,
    "Leather Vest": 1,
    "Silver Key": 1
  },
  "PlayerLog": [
    {"Originator": "Kaelen", "Type": "KillEnemies", "Target": ["Forest Goblin"], "For": "Kaelen", "Received": {"Iron Sword": 1, "Health Potion": 1}, "Favorability": 1},
    {"Originator": "Mira Thornwood", "Type": "RecoverStolenItem", "Target": ["Dwarven Ale"], "For": "Kaelen", "Received": {"Dwarven Ale": 2, "Elven Bread": 1}, "Favorability": 1},
    {"Originator": "Grimgar the Old", "Type": "AttackThreateningEntities", "Target": ["Cultist Fanatic"], "For": "Kaelen", "Received": {"Scroll of Fireball": 1}, "Favorability": 2},
    {"Originator": "Kaelen", "Type": "GuardEntity", "Target": ["Lyra Swiftarrow"], "For": "Lyra Swiftarrow", "Received": {"Mysterious Herb": 2}, "Favorability": 1},
    {"Originator": "Aldric the Wise", "Type": "KillEnemies", "Target": ["Iron Covenant Raider"], "For": "Kaelen", "Received": null, "Favorability": 1},
    {"Originator": "Kaelen", "Type": "StealStuff", "Target": ["Silver Key"], "For": "Kaelen", "Received": {"Silver Key": 1}, "Favorability": -1},
    {"Originator": "Kaelen", "Type": "AttackEnemy", "Target": ["Marsh Troll"], "For": "Kaelen", "Received": {"Healing Poultice": 1}, "Favorability": 0},
    {"Originator": "Lyra Swiftarrow", "Type": "EventTypes", "Target": ["Kaelen", "The Verdant Circle"], "For": "Kaelen", "Received": null, "Favorability": 2},
    {"Originator": "Kaelen", "Type": "RecoverStolenItem", "Target": ["Obsidian Arrowhead"], "For": "Faelan Moonshadow", "Received": {"Obsidian Arrowhead": 3}, "Favorability": 1},
    {"Originator": "Kaelen", "Type": "KillEnemies", "Target": ["Shadow Viper"], "For": "Kaelen", "Received": null, "Favorability": 0}
  ],
  "Location": "Whispering Pines Inn",
  "Skills": [
    {"Name": "Swordsmanship", "Level": 3},
    {"Name": "Stealth", "Level": 2},
    {"Name": "Alchemy", "Level": 1}
  ]
}
;
```