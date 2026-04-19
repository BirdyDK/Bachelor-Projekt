    Now for each of the 50 quests take relavent data for the quest from the game state dataset that could generate that quest and it should be set up like it is in the game state dataset. mutiple quest may use the same data. Note that you are allowed to exclude unrelated relationships on NPCs, Factions, and the Player. And you should exclude alternate names. and exclude empty fields.
    
    example:
    ```
    Quest 1: The Spider Infestation
    json
    {
      "Quest": {
        "Structure": "Attack threatening entities", 
        "Name": "The Spider Infestation", 
        "Giver": "Pippin Thistlefoot", 
        "Reward": {
            "Copper Coin": 25, 
            "Salted Meat": 3
        }, 
        "Favorability": {
            "Pippin Thistlefoot": 5
        }, 
        "Actions": ["goto Whispering Woods", "damage Forest Spider", "goto Verdantia", "report Pippin Thistlefoot"]
      },
      "RelevantData": {
        "NPCs": {
          "Pippin Thistlefoot": {
            "Name": "Pippin Thistlefoot",
            "Species": "Halfling",
            "HomeLocation": "Verdantia",
            "CurrentLocation": "Verdantia",
            "Faction": null,
            "OwnedItems": {
                "Cooking Spices": 2,
                "Salted Meat": 5
            }
            "Role": "Innkeeper",
            "Relations": [
              {"Target": "The Traveler", "Favorability": 15}
            ]
          }
        },
        "Factions": {
            /* only if there are any factions */
        },
        "Locations": {
          "Whispering Woods": {
            "Name": "Whispering Woods",
            "Enemies": ["Forest Spider", "Dire Wolf", "Harpy"],
            "Resources": ["Elven Shortbow", "Glowdust", "Mana Vial", "Elven Bread"]
          },
          "Verdantia": {
            "Name": "Verdantia",
            "Enemies": ["Forest Spider"],
            "Resources": ["Nightshade Petal", "Elven Bread", "Fresh Water"]
          }
        },
        "Enemies": {
          "Forest Spider": {
            "Name": "Forest Spider",
            "Loot": ["Nightshade Petal", "Copper Coin"]
          }
        },
        "Items": {
            "Copper Coin": {
                "Type": "Currency",
                "Name": "Copper Coin"
            },
            "Salted Meat": {
                "Type": "Food",
                "Name": "Salted Meat"
            }
        }
      }
    }
    ```