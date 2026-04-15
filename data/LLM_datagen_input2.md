Based on this data, can you please generate 50 different quests that would be relevant for the player following these rules. 

# Explanation 
Pick a quest from "Quest Structures" and fill the rules until only atomic actions are left. Rules are defined as <RULE> (e.g. <goto> or <kill>) and their use can be found in Rules. Atomic actions are the ones defined in Atomic Actions and are what a quest has to end up as. 

# Atomic Actions 7
| Action | Precondition | Post-Condition | | ---------- | ----------------------------------------------- | ------------------------------------------ | 
| terminal | None. | None. | | damage | Somebody or something is there. | It is more damaged. | 
| defend | Somebody or something is there | Attempts to damage it have failed. | 
| explore | None. | Wander around at random. | 
| gather | Something is there. | You have it. | 
| give | Somebody is there, you have something. | They have it, and you don’t. | 
| goto | You know where to go and how to get there. | You are there. | 
| kill | Somebody is there. | They’re dead. | 
| read | Something is there. | You have information from it. | 
| report | Somebody is there. | They have information that you have. | 
| stealth | Somebody is there. | Sneak up on them. | 
| take | Somebody is there, they have something. | You have it and they don’t. | 

# Rules 
## <goto> 
- <goto> ::= terminal - You are already there. 
- <goto> ::= explore - Just wander around and look. 
- <goto> ::= <learn> goto - Find out where to go and go there. 

## <learn> 
- <learn> ::= terminal - You already know it. 
- <learn> ::= <goto> <get> read - Go someplace, get something, and read what is written on it. 

## <get> 
- <get> ::= terminal - You already have it. 
- <get> ::= <steal> - Steal it from somebody. 
- <get> ::= <goto> gather - Go someplace and pick something up that’s lying around there. 

## <steal> 
- <steal> ::= <goto> stealth take - Go someplace, sneak up on somebody, and take something. 
- <steal> ::= <goto> <kill> take - Go someplace, kill somebody and take something. 

## <kill> 
- <kill> ::= <goto> kill - Go someplace and kill somebody 

# Quest Structures 
## Attack threatening entities 
<goto> damage <goto> report 
This quest structure should mainly target monsters that can be found in the region. It can be given to the player so long as their relation level to the quest giver of -2 or higher.

## Recover stolen item 
<get> <goto> give 
This quest structure can be given by NPCs or Factions with a relation of 3 or higher. The target can be any NPC or Faction they dislike.

## Guard entity 
<goto> defend 
This quest structure can be given by Factions with a relation of 2 or higher. The target can be any NPC in the Faction or a friendly Faction.

## Attack enemy 
<goto> damage 
This quest structure can be given by NPCs or Factions with a relation of 1 or higher. The target can be any Faction or NPC they dislike.

## Steal stuff 
<goto> <steal> <goto> give 
This quest structure can be given by NPCs or Factions with a relation of 2 or higher. The target can be any Item they desire.

## Kill enemies 
<goto> <kill> <goto> report 
This quest structure can only be given by a Faction or NPC with a relation level of 4 or higher, or -4 or lower. This structure is used to kill high-profile targets of oposing Factions or NPCs the quest giver hates, so it's only given to players that the Faction trusts (4 or higher) or to make the player prove that they're willing to go the mile to join them (-4 or lower).

# Output Please output both the json structure and just a list of the atomic actions (skipping terminal) for each quest


example structure:
```
QUEST NAME //Replace with the quest name
Structure: STRUCTURE //Repalce with the chosen quest structure
JSON:
{"Quest": {"Structure":"", "Name": "", "Giver": "NPC", "Reward": {"ITEM": QUANTITY (can be more than one item) }, "Favorability":{"NPC/FACTION":VALUE (can be more than one NPC or Faction, and if someone has been negatively affect it should appear here as well)}, "Actions": [(a list of atomic actions followed by their target, eg. "goto LOCATION")]}}

Description:  //A flavorful description for the quest. It is important that the plurality of topics in the description are correct.
Quest Hook: //A flavorful hook said by the quest giver to the player.
```