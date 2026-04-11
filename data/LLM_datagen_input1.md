You are a video game developer with 15 years of experience. You have to make a full set of game state data that's written in a markdown and json format following this logic:
```md
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
```
It should readable by a csv linter that separates on ';'. 
There should be more than: 
- 50 NPCs 
- 25 Items 
- 10 Locations 
- 5 Factions 
- 20 Enemies 
- 10 Logs for the player, with at least 3 being previously completed quests 

## Relations and Logs 
All logs should relate to the player, whether it's the player completing a quest or killing an NPC or a Faction's member. 

# Rules spec 
## Enums 
There are two categories of enums used. The first is the "Types" category, which is just all available types of the prefix. The second is essentially a list of all the available options for that object. An example would be that NPCs has the names of all NPCs. This is to avoid having looping references in the other objects. 

### Types 
- ItemTypes 
- QuestTypes (AttackThreateningEntities, RecoverStolenItem, GuardEntity, AttackEnemy, StealStuff, KillEnemies) 
- EventTypes 
- RelationshipLevels (Each level needs a name with Sworn Enemy at -50 and Sworn Ally at +50) 

### Lists 
- Species 
- Roles 
- Locations 
- Factions 
- Locations 
- Factions 
- Enemies 
- Items 
- NPCs 
- Player (only has one value) 

## Player 
Species : Species 
FactionRelations : list[Relation] 
NPCRelations : list[Relation] 
PartyMembers : list[NPCs] 
Inventory : dict[Items, int] (the items and amount of them) 
PlayerLog : list[Log] 
Location : Locations 
Skills : list[Skill] 

## NPC 
Name : string 
NamePossessive : string 
Species : Species 
HomeLocation : Locations 
CurrentLocation : Locations 
Faction : Factions 
OwnedItems : dict[Items, int] (the items and amount of them) 
Role : Roles 
Relations : list [Relation] 
NPCLog : list[Log] 

## Location 
Name : string 
NameDefinitive : string
NameDefinitiveCaps : string
NamePossessive : string
NameDefinitivePossessive : string
NameDefinitivePossessiveCaps : string
Enemies : list[Enemies] 
Resources : list[Items] 

## Relation 
Target : Factions | NPCs | Player 
Favorability : RelationshipLevels 

## Faction 
Name : string 
NameDefinitive : string
NameDefinitiveCaps : string
NamePossessive : string
NameDefinitivePossessive : string
NameDefinitivePossessiveCaps : string
DefaultLocation : Locations
Relations : list[Relation] 
Members : list[NPCs] 
Treasury : dict[Items, int] (the items and amount of them) 
FactionLog : list[Log] 

## Skill 
Name : string 
Level : int 

## Enemy 
Name : string 
NameSingular : string
NamePlural : string 
NamePossessiveSingular : string
NamePossessivePlural : string
IndefiniteArticle : string
IndefiniteArticleCaps : string
Loot : list[Items] 

## Item
Type : ItemTypes
Name : string
NameSingular : string
NamePlural : string
NamePossessiveSingular : string
NamePossessivePlural : string
IndefiniteArticle : string
IndefiniteArticleCaps : string

## Log 
Originator : Player | NPCs | Factions | Enemies 
Type : QuestTypes | EventTypes Target : list[Player | NPCs | Factions | Items | Enemies] (This is who's targeted by the quest or event, e.g. the person to be killed) 
For : Player | NPCs | Factions (This is who takes on the quest or event, e.g. the Player) 
Received : dict[Items, int] (the items and amount of them) | None 
Favorability : Dict[NPCs | Factions, int]

# Template
It should follow this template

```
## ENUM DATA
{
  "Types": {
    "ItemTypes": ["Weapon", "Armor", "Potion", "Ingredient", "Key", "Artifact", "Currency"],
    "QuestTypes": ["AttackThreateningEntities", "RecoverStolenItem", "GuardEntity", "AttackEnemy", "StealStuff", "KillEnemies"],
    "EventTypes": ["Ambush", "Discovery", "Betrayal", "Alliance", "TradeRouteOpened", "ResourceDepleted"],
    "RelationshipLevels": {"Sworn Enemy" : -50, "Enemy" : -30, "Hated" : -15, "Disliked" : -5, "Neutral" : 0, "Friendly" : 5, "Friend" : 15, "Ally" : 30, "Sworn Ally" : 50} // For the negative levels, the value has to be at or lower than the value to count for that level. For the positive values it have to be at or above to count for that level. e.g both -4 and 4 are Neutral, -49 is Enemy, both -50 and -70 are sworn enemy, and both 30 and 35 are Friend.
  },
  "Lists": {
    "Species": ["Human", "Elf", "Dwarf", "Orc", "Halfling", "Lizardfolk"],
    "Roles": ["Innkeeper", "Blacksmith", "Merchant", "GuardCaptain", "Apothecary", "Thief", "Wizard", "Ranger", "Bard", "Priest"],
    "Locations": ,
    "Factions": ,
    "Enemies": ,
    "Items": ,
    "NPCs": ,
    "Player": 
  }
}
;
### ITEM DATA
ITEM NAME: { 
  "Type":  , 
  "Name": , 
  "NameSingular": , 
  "NamePlural": ,
  "NamePossessiveSingular": ,
  "NamePossessivePlural": ,
  "IndefiniteArticle": ,// a/an
  "IndefiniteArticleCaps": // A/An

}
ITEM NAME: ...
;
## GAME STATE DATA
### FACTION DATA
FACTION NAME: {
  "Name": , 
  "NameDefinitive": ,
  "NameDefinitiveCaps": ,
  "NamePossessive": ,
  "NameDefinitivePossessive": ,
  "NameDefinitivePossessiveCaps": ,
  "DefaultLocation": ,
  "Relations": [
    {"Target": PLAYER, "Favorability": VALUE}, // Replace PLAYER with whatever the player is named.
    {"Target": FACTION, "Favorability": VALUE}, // Every Faction should have a relation to all other factions.
  ],
  "Members": ,
  "Treasury": {
    "ITEM": QUANTITY, // Every Faction should have at least 5 items.
  },
  "FactionLog": []
}
FACTION NAME: ...
;
### NPC DATA
NPC NAME: {
  "Name": ,
  "NamePossessive": ,
  "Species": ,
  "HomeLocation": ,
  "CurrentLocation": ,
  "Faction": ,
  "OwnedItems": {
    "ITEM NAME": QUANTITY // Every NPC should own at least 2 items.
  },
  "Role": ,
  "Relations": [
    {"Target": "PLAYER", "Favorability": VALUE}, // Replace PLAYER with whatever the player is named.
    {"Target": "FACTION", "Favorability": VALUE}, // Replace FACTION with any faction. Every NPC should have a relation to 1 or 2 different factions.
    {"Target": "NPC", "Favorability": VALUE} // Replace NPC with any other NPC this NPC has a relation to. Every NPC should have at least one relation at -3 or below, and one at +3 or above. They should have a relation to most NPCs in their faction and a few for a disliked faction.
  ],
  "NPCLog": 
}
NPC NAME: ...
;
### ENEMY DATA
ENEMY NAME: {
  "Name": ,
  "Loot": , 
  "NameSingular": , 
  "NamePlural": ,
  "NamePossessiveSingular": ,
  "NamePossessivePlural": ,
  "IndefiniteArticle": , // a/an
  "IndefiniteArticleCaps": / /A/An
}
ENEMY NAME: ...
;
### LOCATION DATA
LOCATION NAME: {
  "Name": ,
  "NameDefinitive": ,
  "NameDefinitiveCaps": ,
  "NamePossessive": ,
  "NameDefinitivePossessive": ,
  "NameDefinitivePossessiveCaps": ,
  "Enemies": ,
  "Resources": 
}
LOCATION NAME: ...
;
## PLAYER DATA
{
  "Species": ,
  "FactionRelations": [
    {"Target": "FACTION", "Favorability": VALUE}, // There should be a relation to all Factions, and it should reflect their relation to the player.
  ],
  "NPCRelations": [
    {"Target": "NPC", "Favorability": VALUE} // There should be a relation to all NPCs, and it should reflect their relation to the player. The relations should span at least the full spectrum of -50 to 50, though they can go both above and below.
  ],
  "PartyMembers": , // Party members needs a positive relation to the player.
  "Inventory": {
    "ITEM NAME": QUANTITY, // The player should have at least 5 items.
  },
  "PlayerLog": [
    {"Originator": "PLAYER", "Type": , "Target": , "For": , "Received": , "Favorability": {"NPC/FACTION" : VALUE, } }, // Replace PLAYER with what you have named the player. Favorability should only change for affected NPCs or factions.
  ],
  "Location": ,
  "Skills": 
}
;
```