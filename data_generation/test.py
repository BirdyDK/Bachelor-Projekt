from typing import Union, TYPE_CHECKING, List, Any, Dict, Optional, Tuple, Set
import random
import json

if TYPE_CHECKING:
    pass

# ============================================================================
# ENHANCED DATA LISTS WITH NAMES
# ============================================================================

class NPC:
    def __init__(self, name: str, title: str, race: str, profession: str, 
                 allies: List[str], enemies: List[str], 
                 interests: List[str], location: str):
        self.name = name
        self.title = title
        self.race = race
        self.profession = profession
        self.allies = allies
        self.enemies = enemies
        self.interests = interests
        self.location = location
    
    def full_title(self) -> str:
        """Returns the full title with name"""
        return f"{self.name} the {self.title}"

# Define NPCs with actual names
NPCS = [
    # Human NPCs
    NPC("Eldric", "Village Elder", "human", "elder", 
        ["human", "dwarf"], ["orc", "goblin", "dark elf"],
        ["protection", "retrieval"], "the village hall"),
    
    NPC("Seraphina", "Captain of the Guard", "human", "guard", 
        ["human", "dwarf", "elf"], ["orc", "goblin", "bandit", "dark elf"],
        ["elimination", "protection"], "the barracks"),
    
    NPC("Thorvin", "Master Blacksmith", "human", "smith", 
        ["human", "dwarf"], ["orc", "goblin", "troll"],
        ["retrieval", "delivery"], "the smithy"),
    
    NPC("Marcus", "Merchant Lord", "human", "merchant", 
        ["human", "halfling"], ["bandit", "orc", "goblin"],
        ["acquisition", "delivery"], "the merchant quarter"),
    
    NPC("Martha", "Grieving Widow", "human", "civilian", 
        ["human"], ["bandit", "orc"],
        ["retrieval", "vengeance"], "her small cottage"),
    
    # Elven NPCs
    NPC("Aelar", "Elven Ambassador", "elf", "diplomat", 
        ["elf", "human"], ["orc", "dark elf", "troll"],
        ["recovery", "investigation"], "the elven embassy"),
    
    NPC("Lyra", "Forest Guardian", "elf", "ranger", 
        ["elf", "druid", "beast"], ["orc", "goblin", "dark elf", "troll"],
        ["elimination", "protection"], "the ancient grove"),
    
    # Dwarven NPCs
    NPC("Borin", "Dwarven Chieftain", "dwarf", "chieftain", 
        ["dwarf", "human"], ["orc", "goblin", "dark elf", "troll"],
        ["recovery", "elimination"], "the mountain halls"),
    
    NPC("Helga", "Master Smith", "dwarf", "smith", 
        ["dwarf", "human"], ["orc", "goblin", "dragon"],
        ["acquisition", "retrieval"], "the deep forge"),
    
    # Orc NPCs
    NPC("Grommash", "Orc Chieftain", "orc", "chieftain", 
        ["orc"], ["human", "elf", "dwarf"],
        ["acquisition", "elimination"], "the orc camp"),
    
    NPC("Mor'gash", "Orc Shaman", "orc", "shaman", 
        ["orc"], ["human", "elf", "dwarf", "paladin"],
        ["recovery", "investigation"], "the ritual grounds"),
    
    # Halfling NPCs
    NPC("Bilbo", "Merchant", "halfling", "merchant", 
        ["halfling", "human"], ["goblin", "bandit"],
        ["delivery", "acquisition"], "the trading post"),
    
    # Gnome NPCs
    NPC("Tinkerbell", "Inventor", "gnome", "inventor", 
        ["gnome", "human"], ["goblin", "troll"],
        ["retrieval", "investigation"], "the workshop"),
]

# Locations with their default inhabitants
LOCATIONS = [
    ("the abandoned mine", ["goblin", "troll"]),
    ("the ancient library", ["spirit", "ghost"]),
    ("the bandit camp", ["bandit"]),
    ("the castle ruins", ["undead"]),
    ("the cursed forest", ["dark elf", "spider"]),
    ("the dark cavern", ["troll", "orc"]),
    ("the dragon's lair", ["dragon"]),
    ("the dwarven halls", ["dwarf"]),
    ("the elven grove", ["elf"]),
    ("the forgotten temple", ["cultist", "undead"]),
    ("the ghost town", ["ghost", "bandit"]),
    ("the goblin warrens", ["goblin"]),
    ("the haunted crypt", ["undead", "ghost"]),
    ("the hidden oasis", ["bandit"]),
    ("the icy peaks", ["troll", "yetis"]),
    ("the king's castle", ["human"]),
    ("the merchant quarter", ["human", "halfling"]),
    ("the misty swamp", ["lizardfolk", "dragon"]),
    ("the monster's den", ["beast"]),
    ("the mountain pass", ["orc", "troll"]),
    ("the old windmill", ["human"]),
    ("the oracle's shrine", ["spirit"]),
    ("the orc camp", ["orc"]),
    ("the pirate cove", ["bandit"]),
    ("the poisoned well", ["beast"]),
    ("the quarry", ["troll"]),
    ("the river crossing", ["bandit"]),
    ("the rogue's gallery", ["thief"]),
    ("the sacred grove", ["elf", "druid"]),
    ("the shadowy alley", ["thief"]),
    ("the shipwreck", ["sea creature"]),
    ("the silver mine", ["dwarf", "troll"]),
    ("the smithy", ["human"]),
    ("the sorcerer's tower", ["mage"]),
    ("the spider caves", ["spider"]),
    ("the tavern", ["human", "halfling"]),
    ("the thief guild", ["thief"]),
    ("the tombs of the ancients", ["undead"]),
    ("the underground river", ["beast"]),
    ("the vampire's castle", ["vampire"]),
    ("the warlock's hut", ["cultist"]),
    ("the werewolf's clearing", ["werewolf"]),
    ("the witch's cottage", ["witch"]),
    ("the wizard's tower", ["mage"]),
]

# Items with descriptions
ITEMS = [
    ("an ancient artifact", "artifact", "a mysterious relic from a bygone age"),
    ("a bag of gold", "treasure", "fifty gleaming gold pieces"),
    ("a ceremonial dagger", "weapon", "a ornate dagger used in rituals"),
    ("a cryptic map", "document", "a weathered map covered in mysterious symbols"),
    ("a cursed amulet", "jewelry", "a dark amulet that seems to pulse with malevolent energy"),
    ("a dragon's egg", "treasure", "a massive egg with scales that shimmer like gems"),
    ("an enchanted sword", "weapon", "a blade that glows with a faint blue light"),
    ("a family heirloom", "treasure", "a precious item passed down through generations"),
    ("a forgotten scroll", "document", "an ancient scroll covered in dust"),
    ("a glowing gemstone", "treasure", "a crystal that emits a soft, pulsing light"),
    ("a golden chalice", "religious", "a beautiful cup adorned with precious gems"),
    ("a healing potion", "potion", "a vial of bubbling red liquid"),
    ("a mysterious key", "tool", "an ornate key of unknown origin"),
    ("a love letter", "document", "a heartfelt letter sealed with wax"),
    ("a lost manuscript", "document", "pages of handwritten text bound in leather"),
    ("a magic ring", "jewelry", "a simple band that hums with power"),
    ("a ornate box", "container", "a beautifully carved wooden box"),
    ("a poisonous herb", "herb", "a dark leaf that smells of decay"),
    ("a rare flower", "herb", "a beautiful bloom that only opens under moonlight"),
    ("a sacred relic", "religious", "a holy symbol of immense importance"),
    ("a silver locket", "jewelry", "a delicate locket with a portrait inside"),
    ("a spellbook", "document", "a tome filled with arcane writings"),
    ("a treasure chest", "container", "a small iron-bound chest"),
    ("a vial of dragon's blood", "potion", "a glass container with smoking red liquid"),
    ("an elven cloak", "clothing", "a silken cloak that seems to shift colors"),
    ("an enchanted quill", "tool", "a feather that writes on its own"),
    ("an old coin", "treasure", "a gold coin from a fallen kingdom"),
    ("ancient tablets", "document", "stone tablets covered in cuneiform"),
    ("the captain's badge", "badge", "a symbol of authority"),
    ("the crown jewels", "treasure", "a stunning collection of royal gems"),
    ("the crystal heart", "treasure", "a heart-shaped crystal that beats slowly"),
    ("the eye of the beholder", "treasure", "a massive gem that seems to watch you"),
    ("the golden feather", "treasure", "a feather made of pure gold"),
    ("the heartstone", "jewelry", "a gem that pulses with warmth"),
    ("the hero's shield", "weapon", "a battered but sturdy shield"),
    ("the king's seal", "document", "a wax seal bearing the royal crest"),
    ("the last will", "document", "a legal document detailing inheritance"),
    ("the moonstone", "jewelry", "a pale stone that glows in darkness"),
    ("the phoenix feather", "treasure", "a feather that smolders with inner fire"),
    ("the queen's ring", "jewelry", "an elegant ring set with sapphires"),
    ("the sun medallion", "jewelry", "a golden disc that warms the skin"),
    ("the warlord's helmet", "weapon", "a fearsome helm with horns"),
]

# Enemies/entities
ENTITIES = [
    ("an ancient dragon", "dragon", "beast"),
    ("a bandit leader", "bandit", "humanoid"),
    ("a cave troll", "troll", "beast"),
    ("a corrupt guard", "guard", "humanoid"),
    ("a cultist", "cultist", "humanoid"),
    ("a dark mage", "mage", "humanoid"),
    ("a death knight", "undead", "undead"),
    ("a demon", "demon", "demon"),
    ("an evil sorcerer", "mage", "humanoid"),
    ("a giant spider", "spider", "beast"),
    ("a goblin chieftain", "goblin", "humanoid"),
    ("a grim reaper", "undead", "undead"),
    ("a harpy", "harpy", "beast"),
    ("a hydra", "hydra", "beast"),
    ("an ice wraith", "undead", "undead"),
    ("a killer beast", "beast", "beast"),
    ("a lich", "undead", "undead"),
    ("a mad scientist", "human", "humanoid"),
    ("a mercenary captain", "mercenary", "humanoid"),
    ("a minotaur", "minotaur", "beast"),
    ("a monstrous scorpion", "beast", "beast"),
    ("a necromancer", "mage", "humanoid"),
    ("an ogre", "ogre", "beast"),
    ("a phantom", "undead", "undead"),
    ("a pirate captain", "bandit", "humanoid"),
    ("a rogue knight", "knight", "humanoid"),
    ("a shadow beast", "beast", "beast"),
    ("a skeletal warrior", "undead", "undead"),
    ("a snake charmer", "human", "humanoid"),
    ("a specter", "undead", "undead"),
    ("a swamp monster", "beast", "beast"),
    ("a thief", "thief", "humanoid"),
    ("a vampire lord", "undead", "undead"),
    ("a venomous serpent", "beast", "beast"),
    ("a warlock", "mage", "humanoid"),
    ("a werewolf", "werewolf", "beast"),
    ("a wicked witch", "witch", "humanoid"),
    ("a wyvern", "wyvern", "beast"),
    ("a zombie horde", "undead", "undead"),
    ("the assassin", "assassin", "humanoid"),
    ("the beast master", "human", "humanoid"),
    ("the dark knight", "knight", "humanoid"),
    ("the forest guardian", "elf", "humanoid"),
    ("the guild master", "human", "humanoid"),
]

# Information types
INFORMATION = [
    ("the creature's weakness", "combat"),
    ("the hidden entrance", "location"),
    ("the ritual instructions", "magic"),
    ("the ancient prophecy", "lore"),
    ("the coded message", "secret"),
    ("the treasure map", "location"),
    ("the enemy's patrol routes", "intel"),
    ("the secret password", "secret"),
    ("the poison recipe", "alchemy"),
    ("the antidote formula", "alchemy"),
    ("the summoning chant", "magic"),
    ("the banishment ritual", "magic"),
    ("the location of the vault", "location"),
    ("the guardian's true name", "lore"),
    ("the cursed words", "magic"),
    ("the blessing incantation", "religion"),
    ("the historical account", "lore"),
    ("the witness testimony", "intel"),
    ("the encrypted letter", "secret"),
    ("the faded diary", "lore"),
    ("the torn parchment", "lore"),
    ("the bloodstained note", "intel"),
    ("the royal decree", "politics"),
    ("the wanted poster", "intel"),
    ("the contract", "legal"),
    ("the deed", "legal"),
    ("the census records", "lore"),
    ("the trade manifest", "commerce"),
    ("the ship's log", "lore"),
    ("the expedition journal", "lore"),
]

# Quest reasons
REASONS = [
    ("to save my village from ruin", "protection"),
    ("to protect the innocent from harm", "protection"),
    ("to guard my caravan from bandits", "protection"),
    ("to defend my temple from desecration", "protection"),
    
    ("to reclaim what was stolen from my family", "retrieval"),
    ("to recover a sacred relic for my order", "retrieval"),
    ("to find a lost artifact I've been seeking", "retrieval"),
    ("to retrieve the stolen documents", "retrieval"),
    
    ("to avenge my fallen brother", "vengeance"),
    ("to stop the impending invasion of our lands", "elimination"),
    ("to eliminate the growing threat to my people", "elimination"),
    ("to put down the beast that's been terrorizing us", "elimination"),
    
    ("to discover the truth about my past", "investigation"),
    ("to uncover the conspiracy against me", "investigation"),
    ("to find out who's behind the attacks on us", "investigation"),
    ("to learn the ancient ritual I need", "investigation"),
    
    ("to prove your worth to my guild", "acquisition"),
    ("to win the heart of my beloved", "acquisition"),
    ("to settle an old debt I owe", "acquisition"),
    ("to fulfill my dying mother's wish", "acquisition"),
    
    ("to lift the curse upon my land", "curse"),
    ("to break the eternal winter that plagues us", "curse"),
    ("to restore the ancient pact we broke", "curse"),
    ("to awaken the sleeping guardian", "curse"),
    
    ("to find a cure for the plague", "rescue"),
    ("to rescue my captured soldiers", "rescue"),
    ("to free the prisoners", "rescue"),
]

# ============================================================================
# QUEST STATE TRACKER
# ============================================================================

class QuestState:
    """Tracks the player's inventory and location throughout the quest"""
    
    def __init__(self, start_location: str):
        self.current_location = start_location
        self.inventory: Set[str] = set()
        self.items_given: Set[str] = set()
        self.locations_visited: Set[str] = {start_location}
        self.actions_log: List[str] = []
        self.location_changed = False
    
    def move_to(self, location: str):
        """Move to a new location (only called from Goto or Explore)"""
        if location != self.current_location:
            self.current_location = location
            self.locations_visited.add(location)
            self.location_changed = True
            self.actions_log.append(f"Moved to {location}")
    
    def add_item(self, item: str):
        """Add item to inventory"""
        self.inventory.add(item)
        self.actions_log.append(f"Acquired {item}")
    
    def remove_item(self, item: str):
        """Remove item from inventory (when given away)"""
        if item in self.inventory:
            self.inventory.remove(item)
            self.items_given.add(item)
            self.actions_log.append(f"Gave away {item}")
    
    def has_item(self, item: str) -> bool:
        """Check if player has an item"""
        return item in self.inventory
    
    def format_location(self, location: str) -> str:
        """Format location with brackets"""
        return f"[{location}]"
    
    def format_item(self, item: str) -> str:
        """Format item with brackets"""
        return f"[{item}]"

# ============================================================================
# ENHANCED ATOMIC ACTION CLASSES
# ============================================================================

class AtomicAction:
    """Base class for atomic actions with data storage"""
    def __init__(self):
        self.data = {}

class Terminal(AtomicAction): 
    pass

class Damage(AtomicAction):
    def __init__(self, target=None):
        super().__init__()
        if target and isinstance(target, tuple):
            self.data["target"] = target[0]
            self.data["target_race"] = target[1]
            self.data["target_type"] = target[2]
        else:
            entity = random.choice(ENTITIES)
            self.data["target"] = entity[0]
            self.data["target_race"] = entity[1]
            self.data["target_type"] = entity[2]

class Defend(AtomicAction):
    def __init__(self, target=None, location=None):
        super().__init__()
        if target and isinstance(target, tuple):
            self.data["target"] = target[0]
            self.data["target_race"] = target[1]
            self.data["target_type"] = target[2]
        else:
            friendly = random.choice([n for n in NPCS if n.race != "orc" and n.race != "goblin"])
            self.data["target"] = friendly.name
            self.data["target_race"] = friendly.race
        
        if location and isinstance(location, tuple):
            self.data["location"] = location[0]
            self.data["location_inhabitants"] = location[1]
        else:
            loc = random.choice(LOCATIONS)
            self.data["location"] = loc[0]
            self.data["location_inhabitants"] = loc[1]

class Explore(AtomicAction):
    def __init__(self, location=None):
        super().__init__()
        if location and isinstance(location, tuple):
            self.data["location"] = location[0]
            self.data["location_inhabitants"] = location[1]
        else:
            loc = random.choice(LOCATIONS)
            self.data["location"] = loc[0]
            self.data["location_inhabitants"] = loc[1]

class Gather(AtomicAction):
    def __init__(self, item=None, location=None):
        super().__init__()
        if item and isinstance(item, tuple):
            self.data["item"] = item[0]
            self.data["item_type"] = item[1]
            self.data["item_desc"] = item[2]
        else:
            it = random.choice(ITEMS)
            self.data["item"] = it[0]
            self.data["item_type"] = it[1]
            self.data["item_desc"] = it[2]
        
        if location and isinstance(location, tuple):
            self.data["location"] = location[0]
            self.data["location_inhabitants"] = location[1]
        else:
            loc = random.choice(LOCATIONS)
            self.data["location"] = loc[0]
            self.data["location_inhabitants"] = loc[1]

class Give(AtomicAction):
    def __init__(self, item=None, recipient=None):
        super().__init__()
        if item and isinstance(item, tuple):
            self.data["item"] = item[0]
            self.data["item_type"] = item[1]
            self.data["item_desc"] = item[2]
        else:
            it = random.choice(ITEMS)
            self.data["item"] = it[0]
            self.data["item_type"] = it[1]
            self.data["item_desc"] = it[2]
        
        if recipient and isinstance(recipient, NPC):
            self.data["recipient"] = recipient.full_title()
            self.data["recipient_race"] = recipient.race
            self.data["recipient_profession"] = recipient.profession
            self.data["recipient_location"] = recipient.location
        else:
            npc = random.choice(NPCS)
            self.data["recipient"] = npc.full_title()
            self.data["recipient_race"] = npc.race
            self.data["recipient_profession"] = npc.profession
            self.data["recipient_location"] = npc.location

class Goto(AtomicAction):
    def __init__(self, location=None):
        super().__init__()
        if location and isinstance(location, tuple):
            self.data["location"] = location[0]
            self.data["location_inhabitants"] = location[1]
        else:
            loc = random.choice(LOCATIONS)
            self.data["location"] = loc[0]
            self.data["location_inhabitants"] = loc[1]

class Kill(AtomicAction):
    def __init__(self, target=None):
        super().__init__()
        if target and isinstance(target, tuple):
            self.data["target"] = target[0]
            self.data["target_race"] = target[1]
            self.data["target_type"] = target[2]
        else:
            entity = random.choice(ENTITIES)
            self.data["target"] = entity[0]
            self.data["target_race"] = entity[1]
            self.data["target_type"] = entity[2]

class Read(AtomicAction):
    def __init__(self, information=None, location=None):
        super().__init__()
        if information and isinstance(information, tuple):
            self.data["information"] = information[0]
            self.data["info_type"] = information[1]
        else:
            info = random.choice(INFORMATION)
            self.data["information"] = info[0]
            self.data["info_type"] = info[1]
        
        if location and isinstance(location, tuple):
            self.data["location"] = location[0]
            self.data["location_inhabitants"] = location[1]
        else:
            loc = random.choice(LOCATIONS)
            self.data["location"] = loc[0]
            self.data["location_inhabitants"] = loc[1]

class Report(AtomicAction):
    def __init__(self, recipient=None, information=None):
        super().__init__()
        if recipient and isinstance(recipient, NPC):
            self.data["recipient"] = recipient.full_title()
            self.data["recipient_race"] = recipient.race
            self.data["recipient_location"] = recipient.location
        else:
            npc = random.choice(NPCS)
            self.data["recipient"] = npc.full_title()
            self.data["recipient_race"] = npc.race
            self.data["recipient_location"] = npc.location
        
        if information:
            self.data["information"] = information
        else:
            self.data["information"] = "what I discovered"

class Stealth(AtomicAction):
    def __init__(self, target=None, location=None):
        super().__init__()
        if target and isinstance(target, tuple):
            self.data["target"] = target[0]
            self.data["target_race"] = target[1]
            self.data["target_type"] = target[2]
        else:
            entity = random.choice(ENTITIES)
            self.data["target"] = entity[0]
            self.data["target_race"] = entity[1]
            self.data["target_type"] = entity[2]
        
        if location and isinstance(location, tuple):
            self.data["location"] = location[0]
            self.data["location_inhabitants"] = location[1]
        else:
            loc = random.choice(LOCATIONS)
            self.data["location"] = loc[0]
            self.data["location_inhabitants"] = loc[1]

class Take(AtomicAction):
    def __init__(self, item=None, owner=None):
        super().__init__()
        if item and isinstance(item, tuple):
            self.data["item"] = item[0]
            self.data["item_type"] = item[1]
            self.data["item_desc"] = item[2]
        else:
            it = random.choice(ITEMS)
            self.data["item"] = it[0]
            self.data["item_type"] = it[1]
            self.data["item_desc"] = it[2]
        
        if owner and isinstance(owner, tuple):
            self.data["owner"] = owner[0]
            self.data["owner_race"] = owner[1]
            self.data["owner_type"] = owner[2]
        else:
            entity = random.choice(ENTITIES)
            self.data["owner"] = entity[0]
            self.data["owner_race"] = entity[1]
            self.data["owner_type"] = entity[2]

# ============================================================================
# RULE CLASSES (UPDATED)
# ============================================================================

class goto_terminal:
    def __init__(self):
        self.terminal = Terminal()

class goto_explore:
    def __init__(self):
        self.explore = Explore()

class goto_learn:
    def __init__(self, learn=None, goto=None):
        self.learn = learn or learn_read()
        self.goto = goto or Goto()

class learn_terminal:
    def __init__(self):
        self.terminal = Terminal()

class learn_read:
    def __init__(self, goto=None, get=None, read=None):
        self.goto = goto or goto_explore()
        self.get = get or get_gather()
        self.read = read or Read()

class get_terminal:
    def __init__(self):
        self.terminal = Terminal()

class get_steal:
    def __init__(self, steal=None):
        self.steal = steal or steal_stealth()

class get_gather:
    def __init__(self, goto=None, gather=None):
        self.goto = goto or goto_explore()
        self.gather = gather or Gather()

class steal_stealth:
    def __init__(self, goto=None, stealth=None, take=None):
        self.goto = goto or goto_explore()
        self.stealth = stealth or Stealth()
        self.take = take or Take()

class steal_kill:
    def __init__(self, goto=None, kill=None, take=None):
        self.goto = goto or goto_explore()
        self.kill = kill or kill_kill()
        self.take = take or Take()

class kill_kill:
    def __init__(self, goto=None, kill=None):
        self.goto = goto or goto_explore()
        self.kill = kill or Kill()

# ============================================================================
# QUEST STRUCTURE CLASSES
# ============================================================================

class AttackThreateningEntities:
    def __init__(self, first_goto=None, damage=None, second_goto=None, report=None):
        self.first_goto = first_goto or goto_learn()
        self.damage = damage or Damage()
        self.second_goto = second_goto or goto_terminal()
        self.report = report or Report()

class RecoverStolenItem:
    def __init__(self, get=None, goto=None, give=None):
        self.get = get or get_steal()
        self.goto = goto or goto_explore()
        self.give = give or Give()

class GuardEntity:
    def __init__(self, goto=None, defend=None):
        self.goto = goto or goto_explore()
        self.defend = defend or Defend()

class AttackEnemy:
    def __init__(self, goto=None, damage=None):
        self.goto = goto or goto_explore()
        self.damage = damage or Damage()

class StealStuff:
    def __init__(self, first_goto=None, steal=None, second_goto=None, give=None):
        self.first_goto = first_goto or goto_terminal()
        self.steal = steal or steal_kill()
        self.second_goto = second_goto or goto_terminal()
        self.give = give or Give()

class KillEnemies:
    def __init__(self, first_goto=None, kill=None, second_goto=None, report=None):
        self.first_goto = first_goto or goto_explore()
        self.kill = kill or kill_kill()
        self.second_goto = second_goto or goto_terminal()
        self.report = report or Report()

# ============================================================================
# QUEST CLASS WITH NPC GIVER
# ============================================================================

class Quest:
    def __init__(self, quest=None, giver=None):
        self.quest = quest
        self.giver = giver or random.choice(NPCS)
        self.reason = None

# ============================================================================
# SMART QUEST GENERATOR
# ============================================================================

class SmartQuestGenerator:
    """Generates quests that make sense for the NPC giving them"""
    
    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth
        self.current_depth = 0
        self.current_giver = None
        self.used_entities = set()
    
    def reset_depth(self):
        self.current_depth = 0
        self.used_entities = set()
    
    def increment_depth(self) -> bool:
        self.current_depth += 1
        return self.current_depth >= self.max_depth
    
    def select_giver(self, quest_type: str) -> NPC:
        """Select an appropriate NPC for the quest type"""
        suitable_npcs = []
        
        for npc in NPCS:
            if quest_type in npc.interests:
                if quest_type == "elimination" and npc.profession in ["guard", "ranger", "chieftain"]:
                    suitable_npcs.extend([npc] * 3)
                elif quest_type == "retrieval" and npc.profession in ["merchant", "smith", "civilian"]:
                    suitable_npcs.extend([npc] * 3)
                elif quest_type == "protection" and npc.profession in ["guard", "elder", "diplomat"]:
                    suitable_npcs.extend([npc] * 3)
                elif quest_type == "acquisition" and npc.profession in ["merchant", "thief"]:
                    suitable_npcs.extend([npc] * 3)
                else:
                    suitable_npcs.append(npc)
        
        if suitable_npcs:
            return random.choice(suitable_npcs)
        else:
            return random.choice(NPCS)
    
    def select_enemy(self, giver: NPC) -> Tuple[str, str, str]:
        """Select an enemy that makes sense for this giver"""
        suitable_enemies = []
        
        for entity in ENTITIES:
            entity_name, entity_race, entity_type = entity
            
            if entity_race in giver.enemies:
                suitable_enemies.extend([entity] * 3)
            
            if entity_race != giver.race or random.random() < 0.1:
                suitable_enemies.append(entity)
        
        if suitable_enemies:
            return random.choice(suitable_enemies)
        else:
            return random.choice(ENTITIES)
    
    def select_friendly_entity(self, giver: NPC) -> Tuple[str, str, str]:
        """Select a friendly entity to protect/help"""
        allies = [e for e in ENTITIES if e[1] in giver.allies]
        if allies:
            return random.choice(allies)
        else:
            neutrals = [e for e in ENTITIES if e[1] not in giver.enemies]
            return random.choice(neutrals) if neutrals else random.choice(ENTITIES)
    
    def select_location(self, giver: NPC, affinity: str = None) -> Tuple[str, List[str]]:
        """Select a location that makes sense"""
        suitable_locations = []
        
        for loc in LOCATIONS:
            loc_name, loc_inhabitants = loc
            
            if affinity == "friendly" and any(inhab in giver.allies for inhab in loc_inhabitants):
                suitable_locations.extend([loc] * 3)
            elif affinity == "enemy" and any(inhab in giver.enemies for inhab in loc_inhabitants):
                suitable_locations.extend([loc] * 3)
            else:
                suitable_locations.append(loc)
        
        if suitable_locations:
            return random.choice(suitable_locations)
        else:
            return random.choice(LOCATIONS)
    
    def select_item(self, giver: NPC, owner_race: str = None) -> Tuple[str, str, str]:
        """Select an item"""
        return random.choice(ITEMS)
    
    def select_reason(self, quest_type: str, giver: NPC) -> str:
        """Select a reason that fits the quest type and giver"""
        suitable_reasons = [r for r in REASONS if r[1] == quest_type]
        
        if giver.profession == "guard" and quest_type == "protection":
            suitable_reasons.append(("to maintain peace in my region", "protection"))
        elif giver.profession == "merchant" and quest_type == "acquisition":
            suitable_reasons.append(("to secure a valuable trade route for myself", "acquisition"))
        elif giver.race == "orc" and quest_type == "elimination":
            suitable_reasons.append(("to prove my strength to the tribe", "elimination"))
        
        if suitable_reasons:
            return random.choice(suitable_reasons)[0]
        else:
            return random.choice(REASONS)[0]
    
    def generate_goto(self, affinity: str = None) -> Union[goto_terminal, goto_explore, goto_learn]:
        """Generate goto with location affinity"""
        if self.increment_depth():
            if random.random() < 0.5:
                return goto_terminal()
            else:
                goto = goto_explore()
                goto.explore = Explore(location=self.select_location(self.current_giver, affinity))
                return goto
        
        choice = random.random()
        if choice < 0.33:
            return goto_terminal()
        elif choice < 0.66:
            goto = goto_explore()
            goto.explore = Explore(location=self.select_location(self.current_giver, affinity))
            return goto
        else:
            goto = goto_learn(
                learn=self.generate_learn(),
                goto=Goto(location=self.select_location(self.current_giver, "friendly"))
            )
            return goto
    
    def generate_learn(self) -> Union[learn_terminal, learn_read]:
        if self.increment_depth():
            return learn_terminal()
        
        if random.random() < 0.3:
            return learn_terminal()
        else:
            return learn_read(
                goto=self.generate_goto(),
                get=self.generate_get(),
                read=Read(location=self.select_location(self.current_giver, "friendly"))
            )
    
    def generate_get(self) -> Union[get_terminal, get_steal, get_gather]:
        if self.increment_depth():
            return get_terminal()
        
        choice = random.random()
        if choice < 0.2:
            return get_terminal()
        elif choice < 0.6:
            return get_steal(steal=self.generate_steal())
        else:
            return get_gather(
                goto=self.generate_goto(),
                gather=Gather(location=self.select_location(self.current_giver, "enemy"))
            )
    
    def generate_steal(self) -> Union[steal_stealth, steal_kill]:
        enemy = self.select_enemy(self.current_giver)
        item = self.select_item(self.current_giver, enemy[1])
        
        if self.increment_depth():
            return steal_stealth(
                goto=self.generate_goto("enemy"),
                stealth=Stealth(target=enemy, location=self.select_location(self.current_giver, "enemy")),
                take=Take(item=item, owner=enemy)
            )
        
        if random.random() < 0.5:
            return steal_stealth(
                goto=self.generate_goto("enemy"),
                stealth=Stealth(target=enemy, location=self.select_location(self.current_giver, "enemy")),
                take=Take(item=item, owner=enemy)
            )
        else:
            return steal_kill(
                goto=self.generate_goto("enemy"),
                kill=self.generate_kill(target=enemy),
                take=Take(item=item, owner=enemy)
            )
    
    def generate_kill(self, target=None) -> kill_kill:
        if not target:
            target = self.select_enemy(self.current_giver)
        
        if self.increment_depth():
            return kill_kill(
                goto=self.generate_goto("enemy"),
                kill=Kill(target=target)
            )
        
        return kill_kill(
            goto=self.generate_goto("enemy"),
            kill=Kill(target=target)
        )
    
    def generate_quest(self) -> Quest:
        self.reset_depth()
        
        quest_categories = {
            "attack_threatening": "elimination",
            "recover_stolen": "retrieval",
            "guard_entity": "protection",
            "attack_enemy": "elimination",
            "steal_stuff": "acquisition",
            "kill_enemies": "elimination"
        }
        
        quest_type_key = random.choice(list(quest_categories.keys()))
        quest_category = quest_categories[quest_type_key]
        
        self.current_giver = self.select_giver(quest_category)
        
        if quest_type_key == "attack_threatening":
            enemy = self.select_enemy(self.current_giver)
            quest_instance = AttackThreateningEntities(
                first_goto=self.generate_goto("friendly"),
                damage=Damage(target=enemy),
                second_goto=self.generate_goto("friendly"),
                report=Report(recipient=self.current_giver)
            )
        elif quest_type_key == "recover_stolen":
            enemy = self.select_enemy(self.current_giver)
            item = self.select_item(self.current_giver, enemy[1])
            quest_instance = RecoverStolenItem(
                get=self.generate_get(),
                goto=self.generate_goto("friendly"),
                give=Give(item=item, recipient=self.current_giver)
            )
        elif quest_type_key == "guard_entity":
            friendly = self.select_friendly_entity(self.current_giver)
            quest_instance = GuardEntity(
                goto=self.generate_goto(),
                defend=Defend(
                    target=friendly,
                    location=self.select_location(self.current_giver, "friendly")
                )
            )
        elif quest_type_key == "attack_enemy":
            enemy = self.select_enemy(self.current_giver)
            quest_instance = AttackEnemy(
                goto=self.generate_goto("enemy"),
                damage=Damage(target=enemy)
            )
        elif quest_type_key == "steal_stuff":
            enemy = self.select_enemy(self.current_giver)
            item = self.select_item(self.current_giver, enemy[1])
            quest_instance = StealStuff(
                first_goto=self.generate_goto("enemy"),
                steal=self.generate_steal(),
                second_goto=self.generate_goto("friendly"),
                give=Give(item=item, recipient=self.current_giver)
            )
        else:  # kill_enemies
            enemy = self.select_enemy(self.current_giver)
            quest_instance = KillEnemies(
                first_goto=self.generate_goto("enemy"),
                kill=self.generate_kill(target=enemy),
                second_goto=self.generate_goto("friendly"),
                report=Report(recipient=self.current_giver, information=f"the death of {enemy[0]}")
            )
        
        quest = Quest(quest=quest_instance, giver=self.current_giver)
        quest.reason = self.select_reason(quest_category, self.current_giver)
        
        return quest

# ============================================================================
# ENHANCED DESCRIPTION GENERATOR WITH STATE TRACKING
# ============================================================================

class QuestDescriptionGenerator:
    """Generates flavorful descriptions from quest structures with state tracking"""
    
    def __init__(self):
        self.state = None
        self.steps = []
        self.current_item = None
    
    def generate_step_by_step(self, obj: Any, steps: list):
        """Generate human-readable steps from the quest structure with state tracking"""
        if obj is None:
            return
        
        match obj:
            # Atomic Actions (ignore Terminal)
            case Damage():
                steps.append(f"Defeat {obj.data['target']} at {self.state.format_location(self.state.current_location)}")
            
            case Defend():
                # Defend happens at the target location, but doesn't move you there
                steps.append(f"Protect {obj.data['target']} at {self.state.format_location(obj.data['location'])}")
                # Note: No state.move_to() - you're already there or will get there via Goto
            
            case Explore():
                # Explore MOVES you to the new location
                steps.append(f"Explore {self.state.format_location(obj.data['location'])}")
                self.state.move_to(obj.data['location'])
            
            case Gather():
                # Gather MOVES you to the location and gives you an item
                steps.append(f"Find {self.state.format_item(obj.data['item'])} at {self.state.format_location(obj.data['location'])}")
                self.state.move_to(obj.data['location'])
                self.state.add_item(obj.data['item'])
            
            case Give():
                # Give happens at the recipient's location, but you need to travel there first
                item = self.state.format_item(obj.data['item'])
                if self.state.has_item(obj.data['item']):
                    steps.append(f"Deliver {item} to {obj.data['recipient']} at {self.state.format_location(obj.data['recipient_location'])}")
                    # Don't move_to here - the Goto before this step already moved you
                    self.state.remove_item(obj.data['item'])
                else:
                    # This shouldn't happen with proper quest structure
                    steps.append(f"ERROR: Don't have {item} to give!")
            
            case Goto():
                # Goto MOVES you to the new location
                steps.append(f"Travel to {self.state.format_location(obj.data['location'])}")
                self.state.move_to(obj.data['location'])
            
            case Kill():
                # Kill happens at current location
                steps.append(f"Slay {obj.data['target']} at {self.state.format_location(self.state.current_location)}")
            
            case Read():
                # Read happens at the location, MOVES you there
                steps.append(f"Read and discover {obj.data['information']} at {self.state.format_location(obj.data['location'])}")
                self.state.move_to(obj.data['location'])
            
            case Report():
                # Report happens at recipient's location, MOVES you there
                steps.append(f"Report back to {obj.data['recipient']} at {self.state.format_location(obj.data['recipient_location'])} about {obj.data['information']}")
                self.state.move_to(obj.data['recipient_location'])
            
            case Stealth():
                # Stealth happens at the location, MOVES you there
                steps.append(f"Sneak past {obj.data['target']} at {self.state.format_location(obj.data['location'])}")
                self.state.move_to(obj.data['location'])
            
            case Take():
                # Take happens at current location, gives you item
                steps.append(f"Take {self.state.format_item(obj.data['item'])} from {obj.data['owner']} at {self.state.format_location(self.state.current_location)}")
                self.state.add_item(obj.data['item'])
            
            # Rule classes - traverse their children
            case (goto_terminal() | goto_explore() | goto_learn() | 
                  learn_terminal() | learn_read() | get_terminal() | 
                  get_steal() | get_gather() | steal_stealth() | 
                  steal_kill() | kill_kill()):
                for value in obj.__dict__.values():
                    if not isinstance(value, Terminal):  # Skip Terminal
                        self.generate_step_by_step(value, steps)
            
            # Quest structures - traverse their children
            case (AttackThreateningEntities() | RecoverStolenItem() | 
                  GuardEntity() | AttackEnemy() | StealStuff() | KillEnemies()):
                for value in obj.__dict__.values():
                    self.generate_step_by_step(value, steps)
            
            # Quest wrapper
            case Quest():
                if hasattr(obj, 'quest'):
                    self.generate_step_by_step(obj.quest, steps)
    
    def generate_description(self, quest: Quest) -> str:
        """Generate a complete quest description with state tracking"""
        
        # Initialize state at the giver's location
        self.state = QuestState(quest.giver.location)
        self.steps = []
        
        # Generate step-by-step instructions
        self.generate_step_by_step(quest, self.steps)
        
        # Build the description
        description = []
        
        # Opening with giver's name and location
        giver = quest.giver
        description.append(f"*{giver.full_title()} finds you at {giver.location}. They lean in close and whisper:*")
        description.append("")
        
        # Quest reason/context (using I/me/my)
        description.append(f"\"{quest.reason.capitalize()}, I need someone with your skills.")
        description.append("")
        
        # The steps - clean up duplicates while preserving order
        seen = set()
        unique_steps = []
        for step in self.steps:
            if step not in seen:
                seen.add(step)
                unique_steps.append(step)
        
        if len(unique_steps) == 1:
            description.append(f"All you need to do is {unique_steps[0].lower()}.")
        else:
            description.append("Here's what needs to be done:")
            for i, step in enumerate(unique_steps, 1):
                description.append(f"{i}. {step}")
        
        description.append("")
        
        # Contextual warnings based on inventory and locations
        if self.state.inventory:
            items_list = ", ".join([self.state.format_item(item) for item in list(self.state.inventory)[:3]])
            description.append(f"Remember, you're carrying {items_list}. Don't lose them!")
        
        if len(self.state.locations_visited) > 1:
            locations_list = ", ".join([self.state.format_location(loc) for loc in list(self.state.locations_visited)[:3]])
            description.append(f"You'll need to travel to {locations_list} along the way.")
        
        description.append("")
        description.append(f"Return to me at {giver.location} when you're done. I'll have your reward ready.\"")
        
        # Race-specific flavor
        race_flavor = {
            "dwarf": " They slap you on the back with a heavy, calloused hand.",
            "elf": " They give you a knowing, mysterious smile.",
            "orc": " They grunt approvingly, showing sharp tusks.",
            "halfling": " They pat your knee warmly, eyes twinkling.",
            "gnome": " They adjust their goggles excitedly."
        }
        
        if giver.race in race_flavor:
            description[-1] = description[-1].replace("\"", f"\"{race_flavor[giver.race]}")
        
        return "\n".join(description)

# ============================================================================
# STRUCTURE PRINTER
# ============================================================================

class QuestStructurePrinter:
    """Prints quest structures with icons"""
    def __init__(self, indent_size: int = 2):
        self.indent_size = indent_size
        self.indent_level = 0
    
    def indent(self) -> str:
        return " " * (self.indent_level * self.indent_size)
    
    def print_with_indent(self, text: str):
        print(f"{self.indent()}{text}")
    
    def traverse(self, obj: Any):
        if obj is None:
            return
        
        match obj:
            case Terminal():
                self.print_with_indent(f"⚡ TERMINAL")
            case Damage():
                self.print_with_indent(f"⚡ DAMAGE ({obj.data['target']})")
            case Defend():
                self.print_with_indent(f"⚡ DEFEND ({obj.data['target']} at {obj.data['location']})")
            case Explore():
                self.print_with_indent(f"⚡ EXPLORE ({obj.data['location']})")
            case Gather():
                self.print_with_indent(f"⚡ GATHER ({obj.data['item']} from {obj.data['location']})")
            case Give():
                self.print_with_indent(f"⚡ GIVE ({obj.data['item']} to {obj.data['recipient']})")
            case Goto():
                self.print_with_indent(f"⚡ GOTO ({obj.data['location']})")
            case Kill():
                self.print_with_indent(f"⚡ KILL ({obj.data['target']})")
            case Read():
                self.print_with_indent(f"⚡ READ ({obj.data['information']} at {obj.data['location']})")
            case Report():
                self.print_with_indent(f"⚡ REPORT (to {obj.data['recipient']} about {obj.data['information']})")
            case Stealth():
                self.print_with_indent(f"⚡ STEALTH (past {obj.data['target']} at {obj.data['location']})")
            case Take():
                self.print_with_indent(f"⚡ TAKE ({obj.data['item']} from {obj.data['owner']})")
            
            # Rule classes
            case goto_terminal():
                self.print_with_indent(f"📋 goto_terminal:")
                self.indent_level += 1
                self.traverse(obj.terminal)
                self.indent_level -= 1
            case goto_explore():
                self.print_with_indent(f"📋 goto_explore:")
                self.indent_level += 1
                self.traverse(obj.explore)
                self.indent_level -= 1
            case goto_learn():
                self.print_with_indent(f"📋 goto_learn:")
                self.indent_level += 1
                self.traverse(obj.learn)
                self.traverse(obj.goto)
                self.indent_level -= 1
            case learn_terminal():
                self.print_with_indent(f"📋 learn_terminal:")
                self.indent_level += 1
                self.traverse(obj.terminal)
                self.indent_level -= 1
            case learn_read():
                self.print_with_indent(f"📋 learn_read:")
                self.indent_level += 1
                self.traverse(obj.goto)
                self.traverse(obj.get)
                self.traverse(obj.read)
                self.indent_level -= 1
            case get_terminal():
                self.print_with_indent(f"📋 get_terminal:")
                self.indent_level += 1
                self.traverse(obj.terminal)
                self.indent_level -= 1
            case get_steal():
                self.print_with_indent(f"📋 get_steal:")
                self.indent_level += 1
                self.traverse(obj.steal)
                self.indent_level -= 1
            case get_gather():
                self.print_with_indent(f"📋 get_gather:")
                self.indent_level += 1
                self.traverse(obj.goto)
                self.traverse(obj.gather)
                self.indent_level -= 1
            case steal_stealth():
                self.print_with_indent(f"📋 steal_stealth:")
                self.indent_level += 1
                self.traverse(obj.goto)
                self.traverse(obj.stealth)
                self.traverse(obj.take)
                self.indent_level -= 1
            case steal_kill():
                self.print_with_indent(f"📋 steal_kill:")
                self.indent_level += 1
                self.traverse(obj.goto)
                self.traverse(obj.kill)
                self.traverse(obj.take)
                self.indent_level -= 1
            case kill_kill():
                self.print_with_indent(f"📋 kill_kill:")
                self.indent_level += 1
                self.traverse(obj.goto)
                self.traverse(obj.kill)
                self.indent_level -= 1
            
            # Quest structures
            case AttackThreateningEntities():
                self.print_with_indent(f"🎯 QUEST: Attack Threatening Entities")
                self.indent_level += 1
                self.traverse(obj.first_goto)
                self.traverse(obj.damage)
                self.traverse(obj.second_goto)
                self.traverse(obj.report)
                self.indent_level -= 1
            case RecoverStolenItem():
                self.print_with_indent(f"🎯 QUEST: Recover Stolen Item")
                self.indent_level += 1
                self.traverse(obj.get)
                self.traverse(obj.goto)
                self.traverse(obj.give)
                self.indent_level -= 1
            case GuardEntity():
                self.print_with_indent(f"🎯 QUEST: Guard Entity")
                self.indent_level += 1
                self.traverse(obj.goto)
                self.traverse(obj.defend)
                self.indent_level -= 1
            case AttackEnemy():
                self.print_with_indent(f"🎯 QUEST: Attack Enemy")
                self.indent_level += 1
                self.traverse(obj.goto)
                self.traverse(obj.damage)
                self.indent_level -= 1
            case StealStuff():
                self.print_with_indent(f"🎯 QUEST: Steal Stuff")
                self.indent_level += 1
                self.traverse(obj.first_goto)
                self.traverse(obj.steal)
                self.traverse(obj.second_goto)
                self.traverse(obj.give)
                self.indent_level -= 1
            case KillEnemies():
                self.print_with_indent(f"🎯 QUEST: Kill Enemies")
                self.indent_level += 1
                self.traverse(obj.first_goto)
                self.traverse(obj.kill)
                self.traverse(obj.second_goto)
                self.traverse(obj.report)
                self.indent_level -= 1
            
            # Quest wrapper
            case Quest():
                self.print_with_indent(f"📦 Quest Wrapper:")
                self.indent_level += 1
                self.print_with_indent(f"👤 Giver: {obj.giver.full_title()}")
                self.print_with_indent(f"📍 Location: {obj.giver.location}")
                if hasattr(obj, 'reason'):
                    self.print_with_indent(f"📝 Reason: {obj.reason}")
                self.traverse(obj.quest)
                self.indent_level -= 1
            
            case _:
                self.print_with_indent(f"❓ Unknown type: {type(obj).__name__}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    printer = QuestStructurePrinter(indent_size=2)
    generator = SmartQuestGenerator(max_depth=4)
    describer = QuestDescriptionGenerator()
    
    # Generate and display 3 random quests
    for i in range(3):
        print(f"\n{'='*70}")
        print(f"RANDOM QUEST {i+1}")
        print(f"{'='*70}")
        
        # Generate smart quest
        random_quest = generator.generate_quest()
        
        # Print tree structure
        print("\n📊 TREE STRUCTURE:")
        printer.traverse(random_quest)
        
        # Print description
        print("\n📝 QUEST DESCRIPTION:")
        print(describer.generate_description(random_quest))
        
        print()