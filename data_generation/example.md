RANDOM QUEST 1
==================================================

📊 TREE STRUCTURE:
📦 Quest Wrapper:
  🎯 QUEST: Attack Threatening Entities
    📋 goto_learn:
      📋 learn_read:
        📋 goto_learn:
          📋 learn_terminal:
            ⚡ TERMINAL
          ⚡ GOTO
        📋 get_terminal:
          ⚡ TERMINAL
        ⚡ READ
      ⚡ GOTO
    ⚡ DAMAGE
    📋 goto_terminal:
      ⚡ TERMINAL
    ⚡ REPORT

📋 JSON FORMAT:
```json
{
  "wrapper": "Quest",
  "quest": {
    "quest": "AttackThreateningEntities",
    "first_goto": {
      "rule": "goto_learn",
      "learn": {
        "rule": "learn_read",
        "goto": {
          "rule": "goto_learn",
          "learn": {
            "rule": "learn_terminal",
            "terminal": {
              "type": "Terminal"
            }
          },
          "goto": {
            "type": "Goto"
          }
        },
        "get": {
          "rule": "get_terminal",
          "terminal": {
            "type": "Terminal"
          }
        },
        "read": {
          "type": "Read"
        }
      },
      "goto": {
        "type": "Goto"
      }
    },
    "damage": {
      "type": "Damage"
    },
    "second_goto": {
      "rule": "goto_terminal",
      "terminal": {
        "type": "Terminal"
      }
    },
    "report": {
      "type": "Report"
    }
  }
}
```

NPC Dialogue:
"There's a growing threat in the ruins to the east. I've heard whispers that something ancient has awakened there, and it's been terrorizing the trade routes. But I don't know exactly where it lairs.

I need you to travel to the old library first—the scholars there have been studying these disturbances. Ask around, find any texts or scrolls that mention ancient guardians in the eastern ruins. Read them carefully to pinpoint the creature's exact location.

Once you've learned where it dwells, head there and put it down. The creature must be destroyed.

After the deed is done, return to me here in town and report what happened. I need to know that the threat is truly gone."

Atomic Actions Breakdown:

GOTO (to library) → READ (scholars' texts) → GOTO (to ruins) → DAMAGE (the creature) → REPORT (to NPC)


RANDOM QUEST 2
==================================================

📊 TREE STRUCTURE:
📦 Quest Wrapper:
  🎯 QUEST: Recover Stolen Item
    📋 get_steal:
      📋 steal_kill:
        📋 goto_terminal:
          ⚡ TERMINAL
        📋 kill_kill:
          📋 goto_explore:
            ⚡ EXPLORE
          ⚡ KILL
        ⚡ TAKE
    📋 goto_explore:
      ⚡ EXPLORE
    ⚡ GIVE

📋 JSON FORMAT:
```json
{
  "wrapper": "Quest",
  "quest": {
    "quest": "RecoverStolenItem",
    "get": {
      "rule": "get_steal",
      "steal": {
        "rule": "steal_kill",
        "goto": {
          "rule": "goto_terminal",
          "terminal": {
            "type": "Terminal"
          }
        },
        "kill": {
          "rule": "kill_kill",
          "goto": {
            "rule": "goto_explore",
            "explore": {
              "type": "Explore"
            }
          },
          "kill": {
            "type": "Kill"
          }
        },
        "take": {
          "type": "Take"
        }
      }
    },
    "goto": {
      "rule": "goto_explore",
      "explore": {
        "type": "Explore"
      }
    },
    "give": {
      "type": "Give"
    }
  }
}
```
NPC Dialogue:
"Those thieving Scorched Hand bandits made off with my grandmother's locket—the only thing I have left of her. I know where their camp is, just north across the river, but they won't give it back peacefully.

Go to their camp and find the brute who's wearing it around his neck. He won't part with it willingly, so... you'll have to be persuasive. Very persuasive. Make sure he's no longer breathing before you take the locket from his corpse.

Once you have it, come find me. I'll be waiting at the old windmill, where I go to be alone. Bring it to me there.

That locket means everything to me. Please, bring it home."

Atomic Actions Breakdown:

GOTO (to bandit camp) → KILL (the bandit) → TAKE (the locket) → GOTO (to windmill) → GIVE (locket to NPC)


RANDOM QUEST 3
==================================================

📊 TREE STRUCTURE:
📦 Quest Wrapper:
  🎯 QUEST: Steal Stuff
    📋 goto_terminal:
      ⚡ TERMINAL
    📋 steal_kill:
      📋 goto_learn:
        📋 learn_terminal:
          ⚡ TERMINAL
        ⚡ GOTO
      📋 kill_kill:
        📋 goto_learn:
          📋 learn_terminal:
          ⚡ TERMINAL
          ⚡ GOTO
        ⚡ KILL
      ⚡ TAKE
    📋 goto_terminal:
      ⚡ TERMINAL
    ⚡ GIVE

📋 JSON FORMAT:
```json
{
  "wrapper": "Quest",
  "quest": {
    "quest": "StealStuff",
    "first_goto": {
      "rule": "goto_terminal",
      "terminal": {
        "type": "Terminal"
      }
    },
    "steal": {
      "rule": "steal_kill",
      "goto": {
        "rule": "goto_learn",
        "learn": {
          "rule": "learn_terminal",
          "terminal": {
            "type": "Terminal"
          }
        },
        "goto": {
          "type": "Goto"
        }
      },
      "kill": {
        "rule": "kill_kill",
        "goto": {
          "rule": "goto_terminal",
          "terminal": {
            "type": "Terminal"
          }
        },
        "kill": {
          "type": "Kill"
        }
      },
      "take": {
        "type": "Take"
      }
    },
    "second_goto": {
      "rule": "goto_learn",
      "learn": {
        "rule": "learn_terminal",
        "terminal": {
          "type": "Terminal"
        }
      },
      "goto": {
        "type": "Goto"
      }
    },
    "give": {
      "type": "Give"
    }
  }
}
```

NPC Dialogue:
"Listen, I need you to do something... discreet. The merchant lord in the manor district has a ceremonial dagger that rightfully belongs to my people. It was taken from our temple decades ago, and I want it back.

Here's what I know: he keeps it in a display case in his study. The manor is heavily guarded, but there's a servant's entrance in the back. Get inside however you can.

The captain of his guard carries the only key to the display case. He's a mean one—won't give it up without a fight. You'll need to deal with him permanently. Search his body for the key, then unlock the case and take the dagger.

Bring it to me at the abandoned shrine in the woods. I'll be waiting there after nightfall.

This dagger is a piece of our history. Bring it back to where it belongs."

Atomic Actions Breakdown:

GOTO (to manor) → KILL (guard captain) → TAKE (key) → TAKE (dagger from case) → GOTO (the abandoned shrine) → GIVE (dagger to NPC at shrine)