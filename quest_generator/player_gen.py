import random
from models import *
from utils import get_new_id

def generate_player(world: WorldState):
    """Generate a player state by simulating past interactions with the world."""
    start_loc = random.choice(list(world.locations.keys()))
    player = PlayerState(
        inventory=[],
        current_location_id=start_loc,
        faction_reputation={faction: 0 for faction in FACTIONS},
        action_log=[],
        completed_quests=[]
    )

    # Simulate random interactions (help/harm/gather/craft)
    num_interactions = random.randint(5, 12)
    for _ in range(num_interactions):
        if random.random() < 0.6 and any(n.alive for n in world.npcs.values()):
            alive_npcs = [n for n in world.npcs.values() if n.alive]
            npc = random.choice(alive_npcs)
            action_type = random.choices(
                ["help", "harm", "neutral"],
                weights=[0.3, 0.3, 0.4]
            )[0]

            if action_type == "help":
                player.faction_reputation[npc.faction] = player.faction_reputation.get(npc.faction, 0) + 1
                event = Event(
                    id=get_new_id(world, "evt"),
                    timestamp=len(player.action_log),
                    type=EventType.HELP,
                    actor_id="player",
                    target_id=npc.id,
                    description=f"Player helped {npc.name}"
                )
                player.action_log.append(event)
                world.events.append(event)

            elif action_type == "harm":
                if random.random() < 0.5 and npc.alive:
                    # Kill
                    npc.alive = False
                    player.faction_reputation[npc.faction] = player.faction_reputation.get(npc.faction, 0) - 3
                    for item_id in npc.inventory:
                        item = world.items[item_id]
                        item.owner_id = npc.location_id
                        item.location_id = npc.location_id
                        world.locations[npc.location_id].items.append(item_id)
                    npc.inventory.clear()
                    event = Event(
                        id=get_new_id(world, "evt"),
                        timestamp=len(player.action_log),
                        type=EventType.KILL,
                        actor_id="player",
                        target_id=npc.id,
                        description=f"Player killed {npc.name}"
                    )
                else:
                    # Steal
                    if npc.inventory:
                        item_id = random.choice(npc.inventory)
                        npc.inventory.remove(item_id)
                        player.inventory.append(item_id)
                        item = world.items[item_id]
                        item.owner_id = "player"
                        item.location_id = None
                        player.faction_reputation[npc.faction] = player.faction_reputation.get(npc.faction, 0) - 1
                        event = Event(
                            id=get_new_id(world, "evt"),
                            timestamp=len(player.action_log),
                            type=EventType.STEAL,
                            actor_id="player",
                            target_id=npc.id,
                            item_id=item_id,
                            description=f"Player stole {item.name} from {npc.name}"
                        )
                    else:
                        continue
                player.action_log.append(event)
                world.events.append(event)
            # neutral: no effect
        else:
            # Player‑only action: gather or craft
            action_type = random.choice(["gather", "craft"])
            if action_type == "gather":
                loc = world.locations[player.current_location_id]
                possible_items = [it for it in world.items.values() if it.type in [ItemType.HERB, ItemType.TOOL] and it.owner_id == loc.id]
                if possible_items:
                    item = random.choice(possible_items)
                    loc.items.remove(item.id)
                    player.inventory.append(item.id)
                    item.owner_id = "player"
                    item.location_id = None
                    event = Event(
                        id=get_new_id(world, "evt"),
                        timestamp=len(player.action_log),
                        type=EventType.GATHER,
                        actor_id="player",
                        item_id=item.id,
                        description=f"Player gathered {item.name} at {loc.name}"
                    )
                    player.action_log.append(event)
                    world.events.append(event)
            elif action_type == "craft":
                if len(player.inventory) >= 2:
                    item1_id = random.choice(player.inventory)
                    item2_id = random.choice([i for i in player.inventory if i != item1_id])
                    player.inventory.remove(item1_id)
                    player.inventory.remove(item2_id)
                    item_id = get_new_id(world, "item")
                    new_item = Item(
                        id=item_id,
                        name="a handcrafted gadget",
                        type=ItemType.CRAFTED,
                        description="A cleverly crafted device",
                        owner_id="player",
                        location_id=None
                    )
                    world.items[item_id] = new_item
                    player.inventory.append(item_id)
                    event = Event(
                        id=get_new_id(world, "evt"),
                        timestamp=len(player.action_log),
                        type=EventType.CRAFT,
                        actor_id="player",
                        item_id=item_id,
                        description=f"Player crafted {new_item.name}"
                    )
                    player.action_log.append(event)
                    world.events.append(event)

    # Simulate completed quests for factions against each other
    num_quests = random.randint(1, 3)
    for _ in range(num_quests):
        giver_faction = random.choice(FACTIONS)
        target_candidates = [
            f for f in FACTIONS
            if f != giver_faction and world.faction_relations[giver_faction].get(f, 0) < 0
        ]
        if not target_candidates:
            target_candidates = [f for f in FACTIONS if f != giver_faction]
        target_faction = random.choice(target_candidates) if target_candidates else random.choice([f for f in FACTIONS if f != giver_faction])

        # Update player reputation
        player.faction_reputation[giver_faction] = player.faction_reputation.get(giver_faction, 0) + 3
        player.faction_reputation[target_faction] = player.faction_reputation.get(target_faction, 0) - 2

        # Record the completed quest in player's completed_quests list
        quest_description = f"Quest for {giver_faction} against {target_faction}"
        player.completed_quests.append(quest_description)

        # Create an event with target_id set to the target faction (as a string)
        event = Event(
            id=get_new_id(world, "evt"),
            timestamp=len(player.action_log),
            type=EventType.QUEST_COMPLETED,
            actor_id="player",
            target_id=target_faction,
            description=f"Player completed a quest for {giver_faction} against {target_faction}"
        )
        player.action_log.append(event)
        world.events.append(event)

    return world, player