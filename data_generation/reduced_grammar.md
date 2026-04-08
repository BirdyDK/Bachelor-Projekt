# Explanation
Pick a quest from "Quest Structures" and fill the rules until only atomic actions are left.
Rules are defined as <RULE> (e.g. <goto> or <kill>) and their use can be found in Rules.
Atomic actions are the ones defined in Atomic Actions and are what a quest has to end up as.


# Atomic Actions
| Action     | Precondition                                    | Post-Condition                             |
| ---------- | ----------------------------------------------- | ------------------------------------------ |
| terminal   | None.                                           | None.                                      |
| damage     | Somebody or something is there.                 | It is more damaged.                        |
| defend     | Somebody or something is there                  | Attempts to damage it have failed.         |
| explore    | None.                                           | Wander around at random.                   |
| gather     | Something is there.                             | You have it.                               |
| give       | Somebody is there, you have something.          | They have it, and you don’t.               |
| goto       | You know where to go and how to get there.      | You are there.                             |
| kill       | Somebody is there.                              | They’re dead.                              |
| read       | Something is there.                             | You have information from it.              |
| report     | Somebody is there.                              | They have information that you have.       |
| stealth    | Somebody is there.                              | Sneak up on them.                          |
| take       | Somebody is there, they have something.         | You have it and they don’t.                |

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

## Recover stolen item
<get> <goto> give

## Guard entity
<goto> defend

## Attack enemy
<goto> damage

## Steal stuff
<goto> <steal> <goto> give

## Kill enemies
<goto> <kill> <goto> report