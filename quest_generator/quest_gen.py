import random
from models import *
from utils import random_choice_weighted

def alive_npcs(world):
    return [n for n in world.npcs.values() if n.alive]

def select_quest_giver(world, player):
    candidates = []
    for npc in alive_npcs(world):
        rep = player.faction_reputation.get(npc.faction, 0)
        weight = max(1, 10 + rep)
        candidates.append((npc, weight))
    return random_choice_weighted(candidates)

def select_enemy(world, player, giver):
    candidates = []
    for npc in alive_npcs(world):
        if npc.id == giver.id:
            continue
        relation = world.faction_relations[giver.faction].get(npc.faction, 0)
        player_rep = player.faction_reputation.get(npc.faction, 0)
        weight = 0
        if relation < 0:
            weight += 5
        if player_rep < -2:
            weight += 4
        if npc.faction != giver.faction:
            weight += 2
        if weight > 0:
            candidates.append((npc, weight))
    if not candidates:
        candidates = [(npc, 1) for npc in alive_npcs(world) if npc.id != giver.id]
    return random_choice_weighted(candidates) if candidates else None

def select_friendly_npc(world, player, giver):
    candidates = []
    for npc in alive_npcs(world):
        if npc.id == giver.id:
            continue
        relation = world.faction_relations[giver.faction].get(npc.faction, 0)
        player_rep = player.faction_reputation.get(npc.faction, 0)
        weight = 1
        if relation > 0:
            weight += 4
        if player_rep > 2:
            weight += 3
        candidates.append((npc, weight))
    return random_choice_weighted(candidates) if candidates else None

def select_item(world, owner_id=None, not_in_player=True):
    candidates = []
    for item in world.items.values():
        if owner_id and item.owner_id != owner_id:
            continue
        if not_in_player and item.owner_id == "player":
            continue
        candidates.append(item)
    return random.choice(candidates) if candidates else None

def select_location(world, affinity=None, giver=None):
    locs = list(world.locations.values())
    return random.choice(locs)

# -------------------- Grammar Generators --------------------
def generate_goto(world, player, giver, purpose=None, max_depth=3):
    if max_depth <= 0:
        return GotoTerminal(terminal=Terminal())
    r = random.random()
    if r < 0.3 or purpose == "terminal":
        return GotoTerminal(terminal=Terminal())
    elif r < 0.7 or purpose == "explore":
        loc = select_location(world)
        return GotoExplore(explore=Explore(location_id=loc.id))
    else:
        learn = generate_learn(world, player, giver, max_depth-1)
        loc = select_location(world)
        goto_atomic = Goto(location_id=loc.id)
        return GotoLearn(learn=learn, goto=goto_atomic)

def generate_learn(world, player, giver, max_depth=3):
    if max_depth <= 0:
        return LearnTerminal(terminal=Terminal())
    r = random.random()
    if r < 0.3:
        return LearnTerminal(terminal=Terminal())
    else:
        goto = generate_goto(world, player, giver, max_depth=max_depth-1)
        get = generate_get(world, player, giver, max_depth=max_depth-1)
        loc = select_location(world)
        read = Read(information="some information", location_id=loc.id)
        return LearnRead(goto=goto, get=get, read=read)

def generate_get(world, player, giver, max_depth=3, target_item=None):
    if max_depth <= 0:
        return GetTerminal(terminal=Terminal())
    r = random.random()
    if r < 0.2:
        return GetTerminal(terminal=Terminal())
    elif r < 0.6:
        steal = generate_steal(world, player, giver, max_depth-1, target_item=target_item)
        return GetSteal(steal=steal)
    else:
        goto = generate_goto(world, player, giver, max_depth=max_depth-1)
        if target_item:
            item = target_item
        else:
            item = select_item(world, not_in_player=True)
        if not item:
            return GetTerminal(terminal=Terminal())
        if item.location_id:
            loc_id = item.location_id
        elif item.owner_id in world.npcs:
            loc_id = world.npcs[item.owner_id].location_id
        else:
            loc_id = random.choice(list(world.locations.keys()))
        gather = Gather(item_id=item.id, location_id=loc_id)
        return GetGather(goto=goto, gather=gather)

def generate_steal(world, player, giver, max_depth=3, target_enemy=None, target_item=None):
    if target_enemy is None:
        target_enemy = select_enemy(world, player, giver)
    if target_enemy is None:
        target_enemy = random.choice(alive_npcs(world))
    if target_item is None:
        target_item = select_item(world, owner_id=target_enemy.id)
    if target_item is None:
        target_item = random.choice(list(world.items.values()))

    if max_depth <= 0:
        goto = generate_goto(world, player, giver, max_depth=max_depth-1)
        stealth = Stealth(target_id=target_enemy.id, location_id=target_enemy.location_id)
        take = Take(item_id=target_item.id, owner_id=target_enemy.id)
        return StealStealth(goto=goto, stealth=stealth, take=take)

    r = random.random()
    if r < 0.5:
        goto = generate_goto(world, player, giver, max_depth=max_depth-1)
        stealth = Stealth(target_id=target_enemy.id, location_id=target_enemy.location_id)
        take = Take(item_id=target_item.id, owner_id=target_enemy.id)
        return StealStealth(goto=goto, stealth=stealth, take=take)
    else:
        goto = generate_goto(world, player, giver, max_depth=max_depth-1)
        kill = generate_kill(world, player, giver, target=target_enemy, max_depth=max_depth-1)
        take = Take(item_id=target_item.id, owner_id=target_enemy.id)
        return StealKill(goto=goto, kill=kill, take=take)

def generate_kill(world, player, giver, target=None, max_depth=3):
    if target is None:
        target = select_enemy(world, player, giver)
    if target is None:
        target = random.choice(alive_npcs(world))
    goto = generate_goto(world, player, giver, max_depth=max_depth-1)
    kill_atomic = Kill(target_id=target.id)
    return KillKill(goto=goto, kill=kill_atomic)

# -------------------- Quest Generators --------------------
def generate_attack_threatening(world, player, giver):
    enemy = select_enemy(world, player, giver)
    first_goto = generate_goto(world, player, giver, purpose="learn")
    damage = Damage(target_id=enemy.id)
    second_goto = generate_goto(world, player, giver, purpose="return")
    report = Report(recipient_id=giver.id, information=f"defeat of {enemy.name}")
    return AttackThreateningEntities(first_goto=first_goto, damage=damage, second_goto=second_goto, report=report)

def generate_recover_stolen(world, player, giver):
    enemy = select_enemy(world, player, giver)
    if enemy is None:
        enemy = random.choice(alive_npcs(world))
    item = select_item(world, owner_id=enemy.id)
    if not item:
        item = select_item(world, not_in_player=True)
    get_rule = generate_get(world, player, giver, target_item=item)
    goto = generate_goto(world, player, giver, purpose="return")
    give = Give(item_id=item.id, recipient_id=giver.id)
    return RecoverStolenItem(get=get_rule, goto=goto, give=give)

def generate_guard_entity(world, player, giver):
    friendly = select_friendly_npc(world, player, giver)
    if friendly is None:
        friendly = random.choice(alive_npcs(world))
    loc = select_location(world)
    goto = generate_goto(world, player, giver)
    defend = Defend(target_id=friendly.id, location_id=loc.id)
    return GuardEntity(goto=goto, defend=defend)

def generate_attack_enemy(world, player, giver):
    enemy = select_enemy(world, player, giver)
    goto = generate_goto(world, player, giver, purpose="enemy")
    damage = Damage(target_id=enemy.id)
    return AttackEnemy(goto=goto, damage=damage)

def generate_steal_stuff(world, player, giver):
    enemy = select_enemy(world, player, giver)
    if enemy is None:
        enemy = random.choice(alive_npcs(world))
    item = select_item(world, owner_id=enemy.id)
    if not item:
        item = select_item(world, not_in_player=True)
    first_goto = generate_goto(world, player, giver, purpose="enemy")
    steal = generate_steal(world, player, giver, target_enemy=enemy, target_item=item)
    second_goto = generate_goto(world, player, giver, purpose="return")
    give = Give(item_id=item.id, recipient_id=giver.id)
    return StealStuff(first_goto=first_goto, steal=steal, second_goto=second_goto, give=give)

def generate_kill_enemies(world, player, giver):
    enemy = select_enemy(world, player, giver)
    if enemy is None:
        enemy = random.choice(alive_npcs(world))
    first_goto = generate_goto(world, player, giver, purpose="enemy")
    kill = generate_kill(world, player, giver, target=enemy)
    second_goto = generate_goto(world, player, giver, purpose="return")
    report = Report(recipient_id=giver.id, information=f"death of {enemy.name}")
    return KillEnemies(first_goto=first_goto, kill=kill, second_goto=second_goto, report=report)

def generate_quest(world, player):
    giver = select_quest_giver(world, player)
    if giver is None:
        alive = alive_npcs(world)
        if not alive:
            raise Exception("No alive NPCs to give quest")
        giver = random.choice(alive)
    quest_types = [
        ("attack_threatening", generate_attack_threatening),
        ("recover_stolen", generate_recover_stolen),
        ("guard_entity", generate_guard_entity),
        ("attack_enemy", generate_attack_enemy),
        ("steal_stuff", generate_steal_stuff),
        ("kill_enemies", generate_kill_enemies),
    ]
    _, gen_func = random.choice(quest_types)
    structure = gen_func(world, player, giver)
    reasons = [
        "to save my village from ruin",
        "to reclaim what was stolen from my family",
        "to avenge my fallen brother",
        "to stop the impending invasion",
        "to prove your worth to my guild",
        "to lift the curse upon my land",
    ]
    reason = random.choice(reasons)
    quest = Quest(giver_id=giver.id, reason=reason, structure=structure)
    return quest