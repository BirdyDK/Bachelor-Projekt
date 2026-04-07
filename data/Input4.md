now put the data generated in a csv file format with the headers input, output, description, Structure. relevant data under input, the quest under output, description under description and Structure under Structure seperated by ;

example:
```
{"NPCs": {
    "Seraphina Dawn": {
        "Name": "Seraphina Dawn", 
        "Species": "Human", 
        "HomeLocation": "Sunstone Temple", 
        "CurrentLocation": "Sunstone Temple", 
        "Faction": "The Sunstone Order", 
        "OwnedItems": {
            "Sunstone Amulet": 1, "Health Potion": 3}, 
            "Role": "Priest", 
            "Relations": [{"Target": "Player", "Favorability": 2}, {"Target": "The Shadow Syndicate", "Favorability": -4}]
    }, 
    "Thorne Blackwood": {
        "Name": "Thorne Blackwood", 
        "Faction": "The Shadow Syndicate", 
        "CurrentLocation": "Shadowfen"
        }
    }, 
    "Locations": {
        "Sunstone Temple": {
            "Name": "Sunstone Temple", 
            "Enemies": [], 
            "Resources": ["Sunstone Amulet", "Health Potion"]
        }, 
        "Shadowfen": {
            "Name": "Shadowfen", 
            "Enemies": ["Shadow Stalker", "Goblin Scavenger"], 
            "Resources": ["Lockpick Set", "Shadowfang Dagger"]
            }
        }, 
    "Factions": {
        "The Shadow Syndicate": {
            "Name": "The Shadow Syndicate", 
            "Relations": [{"Target": "Player", "Favorability": -1}, {"Target": "The Sunstone Order", "Favorability": -5}], 
            "Members": ["Thorne Blackwood"]
        }, 
        "The Sunstone Order": {
            "Name": "The Sunstone Order", 
            "Relations": [{"Target": "The Shadow Syndicate", "Favorability": -5}], 
            "Members": ["Seraphina Dawn"], 
            "Treasury": {"Sunstone Amulet": 3, "Health Potion": 10}
        }
    }
};
{"Quest": {
    "Name": "Sunstone Heist", 
    "Giver": "The Shadow Syndicate", 
    "Actions": ["goto Sunstone Temple", "stealth Seraphina Dawn", "take Sunstone Amulet", "goto Shadowfen", "give Thorne Blackwood"]
    }
};
"The Shadow Syndicate wants you to steal a Sunstone Amulet from the temple to prove your worth.";
"Steal stuff"
```