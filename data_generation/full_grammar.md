# Explanation

# Atomic Actions
| Action     | Precondition                                    | Post-Condition                             |
| ---------- | ----------------------------------------------- | ------------------------------------------ |
| terminal   | None.                                           | None.                                      |
| capture    | Somebody is there.                              | They are your prisoner.                    |
| damage     | Somebody or something is there.                 | It is more damaged.                        |
| defend     | Somebody or something is there                  | Attempts to damage it have failed.         |
| escort     | Somebody is there                               | They will now accompany you.               |
| exchange   | Somebody is there, they and you have something. | You have theirs and they have yours.       |
| experiment | Something is there.                             | Perhaps you have learned what it is for.   |
| explore    | None.                                           | Wander around at random.                   |
| gather     | Something is there.                             | You have it.                               |
| give       | Somebody is there, you have something.          | They have it, and you don’t.               |
| goto       | You know where to go and how to get there.      | You are there.                             |
| kill       | Somebody is there.                              | They’re dead.                              |
| listen     | Somebody is there.                              | You have some of their information.        |
| read       | Something is there.                             | You have information from it.              |
| repair     | Something is there.                             | It is less damaged.                        |
| report     | Somebody is there.                              | They have information that you have.       |
| spy        | Somebody or something is there.                 | You have information about it.             |
| stealth    | Somebody is there.                              | Sneak up on them.                          |
| take       | Somebody is there, they have something.         | You have it and they don’t.                |
| use        | There is something there.                       | It has affected characters or environment. |

# Rules
## <subquest>
- <subquest> ::= <goto> - Subquest could be just to go someplace.
- <subquest> ::= <goto> <QUEST> <goto> - Go perform a quest and return.

## <goto>
- <goto> ::= terminal - You are already there.
- <goto> ::= explore - Just wander around and look.
- <goto> ::= <learn> goto - Find out where to go and go there.

## <learn>
- <learn> ::= terminal - You already know it.
- <learn> ::= <goto> <subquest> <subquest> listen - Go someplace, perform subquest, get info from NPC.
- <learn> ::= <goto> <get> read - Go someplace, get something, and read what is written on it.
- <learn> ::= <get> <subquest> give listen - Get something, perform subquest, give to NPC in return for info

## <get>
- <get> ::= terminal - You already have it.
- <get> ::= <steal> - Steal it from somebody.
- <get> ::= <goto> gather - Go someplace and pick something up that’s lying around there.
- <get> ::= <goto> <get> <goto> <subquest> exchange - Go someplace, get something, do a subquest for somebody, return and exchange.

## <steal>
- <steal> ::= <goto> stealth take - Go someplace, sneak up on somebody, and take something.
- <steal> ::= <goto> <kill> take - Go someplace, kill somebody and take something.

## <spy>
- <spy> ::= <goto> spy <goto> report - Go someplace, spy on somebody, return and report.

## <capture>
- <capture> ::= <get> <goto> capture - Get something, go someplace and use it to capture somebody.

## <kill>
- <kill> ::= <goto> kill - Go someplace and kill somebody

# Quest Structures
## Attack threatening entities
<goto> damage <goto> report

## Recover stolen item
<get> <goto> <give>

## Guard entity
<goto> defend

## Attack enemy
<goto> damage

## Steal stuff
<goto> <steal> <goto> give

## Kill enemies
<goto> <kill> <goto> report