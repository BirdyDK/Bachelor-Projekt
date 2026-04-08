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
- 10 NPCs 
- 10 Items 
- 4 Locations 
- 3 Factions 
- 5 Enemies 
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
- RelationshipLevels (Each level needs a name with Sworn Enemy at -5 and Sworn Ally at +5) 

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
Enemies : list[Enemies] 
Resources : list[Items] 

## Relation 
Target : Factions | NPCs | Player 
Favorability : RelationshipLevels 

## Faction 
Name : string 
Relations : list[Relation] 
Members : list[NPCs] 
Treasury : dict[Items, int] (the items and amount of them) 
FactionLog : list[Log] 

## Skill 
Name : string 
Level : int 

## Enemy 
Name : string 
Loot : list[Items] 

## Log 
Originator : Player | NPCs | Factions | Enemies 
Type : QuestTypes | EventTypes Target : list[Player | NPCs | Factions | Items | Enemies] (This is who's targeted by the quest or event, e.g. the person to be killed) 
For : Player | NPCs | Factions (This is who takes on the quest or event, e.g. the Player) 
Received : dict[Items, int] (the items and amount of them) | None Favorability : int