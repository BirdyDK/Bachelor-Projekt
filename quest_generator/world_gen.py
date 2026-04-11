import random
from models import *
from utils import get_new_id, random_choice_weighted

# Predefined lists for names
NPC_NAMES = [
    "Eldric", "Seraphina", "Thorvin", "Marcus", "Martha", "Aelar", "Lyra",
    "Borin", "Helga", "Grommash", "Mor'gash", "Bilbo", "Tinkerbell"
]
LOCATION_NAMES = [
    "the abandoned mine", "the ancient library", "the bandit camp", "the castle ruins",
    "the cursed forest", "the dark cavern", "the dragon's lair", "the dwarven halls",
    "the elven grove", "the forgotten temple", "the ghost town", "the goblin warrens",
    "the haunted crypt", "the hidden oasis", "the icy peaks", "the king's castle",
    "the merchant quarter", "the misty swamp", "the monster's den", "the mountain pass",
    "the old windmill", "the oracle's shrine", "the orc camp", "the pirate cove",
    "the poisoned well", "the quarry", "the river crossing", "the rogue's gallery",
    "the sacred grove", "the shadowy alley", "the shipwreck", "the silver mine",
    "the smithy", "the sorcerer's tower", "the spider caves", "the tavern",
    "the thief guild", "the tombs of the ancients", "the underground river",
    "the vampire's castle", "the warlock's hut", "the werewolf's clearing",
    "the witch's cottage", "the wizard's tower"
]
ITEM_NAMES = [
    ("an ancient artifact", ItemType.ARTIFACT),
    ("a bag of gold", ItemType.TREASURE),
    ("a ceremonial dagger", ItemType.WEAPON),
    ("a cryptic map", ItemType.DOCUMENT),
    ("a cursed amulet", ItemType.JEWELRY),
    ("a dragon's egg", ItemType.TREASURE),
    ("an enchanted sword", ItemType.WEAPON),
    ("a family heirloom", ItemType.TREASURE),
    ("a forgotten scroll", ItemType.DOCUMENT),
    ("a glowing gemstone", ItemType.TREASURE),
    ("a golden chalice", ItemType.RELIGIOUS),
    ("a healing potion", ItemType.POTION),
    ("a mysterious key", ItemType.TOOL),
    ("a love letter", ItemType.DOCUMENT),
    ("a lost manuscript", ItemType.DOCUMENT),
    ("a magic ring", ItemType.JEWELRY),
    ("a ornate box", ItemType.CONTAINER),
    ("a poisonous herb", ItemType.HERB),
    ("a rare flower", ItemType.HERB),
    ("a sacred relic", ItemType.RELIGIOUS),
    ("a silver locket", ItemType.JEWELRY),
    ("a spellbook", ItemType.DOCUMENT),
    ("a treasure chest", ItemType.CONTAINER),
    ("a vial of dragon's blood", ItemType.POTION),
    ("an elven cloak", ItemType.CLOTHING),
    ("an enchanted quill", ItemType.TOOL),
    ("an old coin", ItemType.TREASURE),
    ("ancient tablets", ItemType.DOCUMENT),
    ("the captain's badge", ItemType.BADGE),
    ("the crown jewels", ItemType.TREASURE),
    ("the crystal heart", ItemType.TREASURE),
    ("the eye of the beholder", ItemType.TREASURE),
    ("the golden feather", ItemType.TREASURE),
    ("the heartstone", ItemType.JEWELRY),
    ("the hero's shield", ItemType.WEAPON),
    ("the king's seal", ItemType.DOCUMENT),
    ("the last will", ItemType.DOCUMENT),
    ("the moonstone", ItemType.JEWELRY),
    ("the phoenix feather", ItemType.TREASURE),
    ("the queen's ring", ItemType.JEWELRY),
    ("the sun medallion", ItemType.JEWELRY),
    ("the warlord's helmet", ItemType.WEAPON),
]

def generate_faction_relations():
    """Create a random relation matrix between factions."""
    relations = {}
    for f in FACTIONS:
        relations[f] = {}
        for other in FACTIONS:
            if f == other:
                relations[f][other] = 0
            else:
                relations[f][other] = random.randint(-3, 3)
    return relations

def generate_world_event(world):
    """Generate a random event between NPCs (or factions) and log it."""
    if len(world.npcs) < 2:
        return
    event_type = random.choice([EventType.FIGHT, EventType.TRADE, EventType.ALLIANCE, EventType.CONFLICT])
    npc1 = random.choice(list(world.npcs.values()))
    npc2 = random.choice([n for n in world.npcs.values() if n.id != npc1.id])
    timestamp = len(world.events)

    if event_type == EventType.FIGHT:
        winner = random.choice([npc1, npc2])
        loser = npc2 if winner == npc1 else npc1
        if random.random() < 0.3:
            loser.alive = False
            for item_id in loser.inventory:
                item = world.items[item_id]
                item.owner_id = loser.location_id
                item.location_id = loser.location_id
                world.locations[loser.location_id].items.append(item_id)
            loser.inventory.clear()
            desc = f"{winner.name} killed {loser.name} in a fight"
            world.faction_relations[winner.faction][loser.faction] -= 1
            world.faction_relations[loser.faction][winner.faction] -= 1
        else:
            desc = f"{npc1.name} fought {npc2.name}"
        evt = Event(
            id=get_new_id(world, "evt"),
            timestamp=timestamp,
            type=EventType.FIGHT,
            actor_id=npc1.id,
            target_id=npc2.id,
            description=desc
        )
        world.events.append(evt)

    elif event_type == EventType.TRADE:
        if npc1.inventory and npc2.inventory:
            item1_id = random.choice(npc1.inventory)
            item2_id = random.choice(npc2.inventory)
            npc1.inventory.remove(item1_id)
            npc2.inventory.remove(item2_id)
            npc1.inventory.append(item2_id)
            npc2.inventory.append(item1_id)
            world.items[item1_id].owner_id = npc2.id
            world.items[item2_id].owner_id = npc1.id
            desc = f"{npc1.name} traded {world.items[item1_id].name} with {npc2.name} for {world.items[item2_id].name}"
        else:
            desc = f"{npc1.name} and {npc2.name} tried to trade but had nothing"
        evt = Event(
            id=get_new_id(world, "evt"),
            timestamp=timestamp,
            type=EventType.TRADE,
            actor_id=npc1.id,
            target_id=npc2.id,
            description=desc
        )
        world.events.append(evt)

    elif event_type == EventType.ALLIANCE:
        if npc2.faction not in npc1.allies:
            npc1.allies.append(npc2.faction)
        if npc1.faction not in npc2.allies:
            npc2.allies.append(npc1.faction)
        world.faction_relations[npc1.faction][npc2.faction] += 1
        world.faction_relations[npc2.faction][npc1.faction] += 1
        evt = Event(
            id=get_new_id(world, "evt"),
            timestamp=timestamp,
            type=EventType.ALLIANCE,
            actor_id=npc1.id,
            target_id=npc2.id,
            description=f"{npc1.name} and {npc2.name} formed an alliance"
        )
        world.events.append(evt)

    elif event_type == EventType.CONFLICT:
        if npc2.faction not in npc1.enemies:
            npc1.enemies.append(npc2.faction)
        if npc1.faction not in npc2.enemies:
            npc2.enemies.append(npc1.faction)
        world.faction_relations[npc1.faction][npc2.faction] -= 1
        world.faction_relations[npc2.faction][npc1.faction] -= 1
        evt = Event(
            id=get_new_id(world, "evt"),
            timestamp=timestamp,
            type=EventType.CONFLICT,
            actor_id=npc1.id,
            target_id=npc2.id,
            description=f"{npc1.name} and {npc2.name} became enemies"
        )
        world.events.append(evt)

def generate_world(num_npcs=8, num_locations=6, num_items=15):
    world = WorldState(
        npcs={},
        locations={},
        items={},
        events=[],
        faction_relations=generate_faction_relations(),
        next_id=0
    )

    # Generate locations
    loc_ids = []
    for i in range(num_locations):
        loc_id = get_new_id(world, "loc")
        name = random.choice(LOCATION_NAMES)
        world.locations[loc_id] = Location(id=loc_id, name=name)
        loc_ids.append(loc_id)

    # Generate NPCs
    for i in range(num_npcs):
        npc_id = get_new_id(world, "npc")
        name = random.choice(NPC_NAMES)
        race = random.choice(list(Race))
        profession = random.choice(list(Profession))
        location_id = random.choice(loc_ids)
        faction = random.choice(FACTIONS)
        # Allies/enemies based on faction relations
        allies = [f for f in FACTIONS if world.faction_relations[faction].get(f, 0) > 0]
        enemies = [f for f in FACTIONS if world.faction_relations[faction].get(f, 0) < 0]
        world.npcs[npc_id] = NPC(
            id=npc_id, name=name, race=race, profession=profession,
            location_id=location_id, faction=faction, allies=allies, enemies=enemies
        )
        world.locations[location_id].inhabitants.append(npc_id)

    # Generate items
    for i in range(num_items):
        item_id = get_new_id(world, "item")
        name, item_type = random.choice(ITEM_NAMES)
        desc = f"A {name}"
        if random.random() < 0.7 and world.npcs:
            owner_id = random.choice(list(world.npcs.keys()))
            owner_type = "npc"
        else:
            owner_id = random.choice(loc_ids)
            owner_type = "location"
        item = Item(id=item_id, name=name, type=item_type, description=desc,
                    owner_id=owner_id, location_id=owner_id if owner_type=="location" else None)
        world.items[item_id] = item
        if owner_type == "npc":
            world.npcs[owner_id].inventory.append(item_id)
        else:
            world.locations[owner_id].items.append(item_id)

    # Generate initial world events
    num_events = random.randint(3, 8)
    for _ in range(num_events):
        generate_world_event(world)

    return world