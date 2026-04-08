import json
import random
import re

# -------------------------
# CONFIG
# -------------------------
ATOMIC_ACTIONS = {
    "terminal", "damage", "defend", "explore", "gather",
    "give", "goto", "kill", "read", "report",
    "stealth", "take"
}

QUEST_STRUCTURES = {
    "AttackThreateningEntities": ["<goto>", "damage", "<goto>", "report"],
    "RecoverStolenItem": ["<get>", "<goto>", "give"],
    "GuardEntity": ["<goto>", "defend"],
    "AttackEnemy": ["<goto>", "damage"],
    "StealStuff": ["<goto>", "<steal>", "<goto>", "give"],
    "KillEnemies": ["<goto>", "<kill>", "<goto>", "report"]
}

# -------------------------
# LOAD WORLD STATE
# -------------------------
def load_world_state(file_path):
    with open(file_path, "r") as f:
        raw = f.read()

    sections = raw.split(";")
    data = {}

    for section in sections:
        if "NPC DATA" in section:
            data["npcs"] = parse_named_json(section)
        elif "FACTION DATA" in section:
            data["factions"] = parse_named_json(section)
        elif "ENEMY DATA" in section:
            data["enemies"] = parse_named_json(section)
        elif "PLAYER DATA" in section:
            player_json = re.search(r'Player:\s*(\{.*\})', section, re.DOTALL)
            if player_json:
                data["player"] = json.loads(player_json.group(1))

    return data


def parse_named_json(section):
    result = {}
    matches = re.findall(r'(\w+):\s*(\{.*?\})(?=;\n|\n|$)', section, re.DOTALL)
    for name, obj in matches:
        result[name] = json.loads(obj)
    return result


# -------------------------
# RULE EXPANSION
# -------------------------
def expand_rule(rule, context):
    """Recursively expand rules into atomic actions"""
    
    if rule == "<goto>":
        return expand_goto(context)

    if rule == "<learn>":
        return expand_learn(context)

    if rule == "<get>":
        return expand_get(context)

    if rule == "<steal>":
        return expand_steal(context)

    if rule == "<kill>":
        return expand_kill(context)

    return [rule]


def expand_goto(context):
    choice = random.choice(["terminal", "explore", "learn"])

    if choice == "terminal":
        return []

    if choice == "explore":
        return ["explore"]

    if choice == "learn":
        return expand_rule("<learn>", context) + ["goto " + context["location"]]


def expand_learn(context):
    choice = random.choice(["terminal", "full"])

    if choice == "terminal":
        return []

    return (
        expand_rule("<goto>", context)
        + expand_rule("<get>", context)
        + ["read"]
    )


def expand_get(context):
    choice = random.choice(["terminal", "steal", "gather"])

    if choice == "terminal":
        return []

    if choice == "steal":
        return expand_rule("<steal>", context)

    if choice == "gather":
        return expand_rule("<goto>", context) + ["gather " + context["item"]]


def expand_steal(context):
    choice = random.choice(["stealth", "kill"])

    if choice == "stealth":
        return (
            expand_rule("<goto>", context)
            + ["stealth " + context["target"]]
            + ["take " + context["item"]]
        )

    return (
        expand_rule("<goto>", context)
        + expand_rule("<kill>", context)
        + ["take " + context["item"]]
    )


def expand_kill(context):
    return expand_rule("<goto>", context) + ["kill " + context["target"]]


# -------------------------
# QUEST GENERATION
# -------------------------
def choose_quest(world):
    player = world["player"]

    # Pick hostile NPC or fallback enemy
    hostile_npcs = [
        rel["Target"] for rel in player["NPCRelations"]
        if rel["Favorability"] < 0
    ]

    if hostile_npcs:
        target = random.choice(hostile_npcs)
        structure = "KillEnemies"
        item = "Gold Coin"
    else:
        target = random.choice(list(world["enemies"].keys()))
        structure = "AttackEnemy"
        item = "Gold Coin"

    quest_giver = random.choice(list(world["npcs"].keys()))
    location = world["player"]["Location"]

    return {
        "target": target,
        "item": item,
        "location": location,
        "giver": quest_giver,
        "structure": structure
    }


def generate_steps(structure, context):
    steps = []

    for part in QUEST_STRUCTURES[structure]:
        if part.startswith("<"):
            steps.extend(expand_rule(part, context))
        else:
            if part == "damage":
                steps.append(f"damage {context['target']}")
            elif part == "report":
                steps.append(f"report {context['giver']}")
            elif part == "give":
                steps.append(f"give {context['giver']} {context['item']}")
            else:
                steps.append(part)

    return steps


def generate_quest(world):
    context = choose_quest(world)

    steps = generate_steps(context["structure"], context)

    return {
        "Name": f"{context['structure']} involving {context['target']}",
        "QuestGiver": context["giver"],
        "Structure": context["structure"],
        "Steps": steps
    }


# -------------------------
# MAIN
# -------------------------
if __name__ == "__main__":
    world = load_world_state("world_state.csv")

    quest = generate_quest(world)

    print(json.dumps(quest, indent=2))