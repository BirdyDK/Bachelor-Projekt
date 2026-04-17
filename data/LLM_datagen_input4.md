now put the data generated in a csv file format with the headers input, output, description, hook, Structure. relevant data under input, the quest under output, description under description, the hook under hook, and Structure under Structure seperated by ;

example:
```
{"NPCs": {
      "Pippin Thistlefoot": {
        "Name": "Pippin Thistlefoot",
        "NamePossessive": "Pippin Thistlefoot's",
        "Species": "Halfling",
        "HomeLocation": "Verdantia",
        "CurrentLocation": "Verdantia",
        "Faction": null,
        "Role": "Innkeeper",
        "Relations": [
          {"Target": "The Traveler", "Favorability": 15}
        ]
      }
    },
    "Locations": {
      "Whispering Woods": {
        "Name": "Whispering Woods",
        "NameDefinitive": "the Whispering Woods",
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
        "NamePlural": "forest spiders",
        "Loot": ["Nightshade Petal", "Copper Coin"]
      }
    }
};
{"Quest": {
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
  }
};
"Pippin Thistlefoot, the innkeeper of Verdantia, is worried about the increasing number of forest spiders creeping closer to the village. Several of his regulars have reported being attacked on the road to the Whispering Woods. Pippin needs someone to thin out the spider population and report back. He's offering a pouch of copper coins and some salted meat from his pantry as payment.";
"Ah, Traveler! Just the person I was hoping to see. Those eight-legged freaks are getting bolder by the day—I found one in my root cellar last night! Could you head into the Whispering Woods and deal with a few forest spiders? Nothing too fancy, just make sure they think twice before skittering toward Verdantia again. I'll make it worth your while.";
"Attack threatening entities"
```