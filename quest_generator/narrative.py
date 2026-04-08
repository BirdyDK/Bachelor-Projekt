from models import *
import random

def get_npc_name(world, npc_id):
    return world.npcs[npc_id].name if npc_id in world.npcs else "someone"

def get_item_name(world, item_id):
    return world.items[item_id].name if item_id in world.items else "something"

def get_location_name(world, loc_id):
    return world.locations[loc_id].name if loc_id in world.locations else "somewhere"

def extract_atomic_actions(quest_node):
    """Recursively traverse quest structure and return list of atomic action names in order."""
    actions = []
    if isinstance(quest_node, AtomicAction):
        actions.append(type(quest_node).__name__.lower())
    elif hasattr(quest_node, '__dict__'):
        for field_name, value in quest_node.__dict__.items():
            if isinstance(value, list):
                for item in value:
                    actions.extend(extract_atomic_actions(item))
            else:
                actions.extend(extract_atomic_actions(value))
    return actions

def safe_extract_string(val):
    if isinstance(val, str):
        return val
    if isinstance(val, dict):
        if 'value' in val:
            return val['value']
        if '_value_' in val:
            return val['_value_']
    return str(val)

def build_lookup(world_dict):
    npc_names = {}
    npc_desc = {}
    for nid, data in world_dict.get("npcs", {}).items():
        name = data.get("name", nid)
        race = safe_extract_string(data.get("race", "unknown"))
        prof = safe_extract_string(data.get("profession", "unknown"))
        faction = data.get("faction", "unknown")
        npc_names[nid] = name
        npc_desc[nid] = f"[{faction} {race} {prof}] {name}"
    loc_names = {lid: data.get("name", lid) for lid, data in world_dict.get("locations", {}).items()}
    item_names = {iid: data.get("name", iid) for iid, data in world_dict.get("items", {}).items()}
    return npc_names, npc_desc, loc_names, item_names

def format_event(evt, npc_desc, item_names, npc_names):
    evt_type = safe_extract_string(evt.get("type", "unknown"))
    actor = evt.get("actor_id", "?")
    target = evt.get("target_id")
    item = evt.get("item_id")

    actor_str = "player" if actor == "player" else npc_desc.get(actor, npc_names.get(actor, actor))
    target_str = npc_desc.get(target, npc_names.get(target, target)) if target else ""
    item_str = item_names.get(item, item) if item else ""

    if evt_type == "kill":
        return f"{actor_str} killed {target_str}"
    elif evt_type == "steal":
        return f"{actor_str} stole {item_str} from {target_str}"
    elif evt_type == "give":
        return f"{actor_str} gave {item_str} to {target_str}"
    elif evt_type == "help":
        return f"{actor_str} helped {target_str}"
    elif evt_type == "quest_given":
        return f"{actor_str} gave a quest to {target_str}"
    elif evt_type == "quest_completed":
        return f"{actor_str} completed a quest for {target_str}"
    elif evt_type == "gather":
        return f"{actor_str} gathered {item_str}"
    elif evt_type == "craft":
        return f"{actor_str} crafted {item_str}"
    elif evt_type == "fight":
        return f"{actor_str} fought {target_str}"
    elif evt_type == "alliance":
        return f"{actor_str} allied with {target_str}"
    elif evt_type == "conflict":
        return f"{actor_str} became enemies with {target_str}"
    elif evt_type == "trade":
        return f"{actor_str} traded with {target_str}"
    else:
        return f"{actor_str} performed {evt_type} on {target_str}"

def generate_narrative(quest, world, player):
    giver = world.npcs[quest.giver_id]
    lines = []
    lines.append(f"*{giver.name} the {giver.profession.value} finds you at {get_location_name(world, giver.location_id)}. They lean in close and whisper:*")
    lines.append("")
    lines.append(f"\"{quest.reason.capitalize()}, I need someone with your skills.\"")
    lines.append("")

    quest_type = type(quest.structure).__name__
    if quest_type == "KillEnemies":
        enemy_id = quest.structure.kill.kill.target_id
        enemy_name = get_npc_name(world, enemy_id)
        lines.append(f"I need you to travel to a dangerous place, slay {enemy_name}, and return to me.")
    elif quest_type == "StealStuff":
        item_id = quest.structure.give.item_id
        item_name = get_item_name(world, item_id)
        lines.append(f"I need you to steal {item_name} from someone and bring it back to me.")
    elif quest_type == "RecoverStolenItem":
        item_id = quest.structure.give.item_id
        item_name = get_item_name(world, item_id)
        lines.append(f"I need you to recover {item_name} that was stolen from me.")
    elif quest_type == "AttackEnemy":
        enemy_id = quest.structure.damage.target_id
        enemy_name = get_npc_name(world, enemy_id)
        lines.append(f"I need you to find and attack {enemy_name}.")
    elif quest_type == "GuardEntity":
        target_id = quest.structure.defend.target_id
        target_name = get_npc_name(world, target_id)
        lines.append(f"I need you to guard {target_name} at a specific location.")
    else:
        lines.append("I have a task for you. Follow my instructions carefully.")

    lines.append("")
    lines.append(f"Return to me at {get_location_name(world, giver.location_id)} when you're done. I'll have your reward ready.\"")

    flavor = {
        Race.DWARF: " They slap you on the back with a heavy, calloused hand.",
        Race.ELF: " They give you a knowing, mysterious smile.",
        Race.ORC: " They grunt approvingly, showing sharp tusks.",
        Race.HALFLING: " They pat your knee warmly, eyes twinkling.",
        Race.GNOME: " They adjust their goggles excitedly."
    }
    if giver.race in flavor:
        lines[-1] = lines[-1].replace("\"", f"\"{flavor[giver.race]}")

    return "\n".join(lines)