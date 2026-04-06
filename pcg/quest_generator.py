import random
from typing import Dict, Any, List, Tuple, Optional
from world_state import WorldState

class QuestGenerator:
    def __init__(self, world_state: WorldState):
        self.ws = world_state
        self.eligible_quests = []

    def compute_eligible_quests(self):
        self.eligible_quests = []
        for npc_name in self.ws.npcs:
            relation = self.ws.get_relation("npc", npc_name)
            if relation >= -2:
                self.eligible_quests.append(("npc", npc_name, "AttackThreateningEntities"))
            if relation >= 3:
                self.eligible_quests.append(("npc", npc_name, "RecoverStolenItem"))
            if relation >= 1:
                self.eligible_quests.append(("npc", npc_name, "AttackEnemy"))
            if relation >= 2:
                self.eligible_quests.append(("npc", npc_name, "StealStuff"))
            if relation >= 4 or relation <= -4:
                self.eligible_quests.append(("npc", npc_name, "KillEnemies"))

        for faction_name in self.ws.factions:
            relation = self.ws.get_relation("faction", faction_name)
            if relation >= -2:
                self.eligible_quests.append(("faction", faction_name, "AttackThreateningEntities"))
            if relation >= 3:
                self.eligible_quests.append(("faction", faction_name, "RecoverStolenItem"))
            if relation >= 2:
                self.eligible_quests.append(("faction", faction_name, "GuardEntity"))
            if relation >= 1:
                self.eligible_quests.append(("faction", faction_name, "AttackEnemy"))
            if relation >= 2:
                self.eligible_quests.append(("faction", faction_name, "StealStuff"))
            if relation >= 4 or relation <= -4:
                self.eligible_quests.append(("faction", faction_name, "KillEnemies"))

    def generate_quest(self, giver_type: str, giver_name: str, quest_type: str) -> Optional[Dict[str, Any]]:
        method_name = f"_generate_{quest_type}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(giver_type, giver_name)
        return None

    def generate_all_quests(self) -> Dict[str, List[Dict[str, Any]]]:
        if not self.eligible_quests:
            self.compute_eligible_quests()
        result = {qt: [] for qt in ["AttackThreateningEntities", "RecoverStolenItem", "GuardEntity",
                                    "AttackEnemy", "StealStuff", "KillEnemies"]}
        for giver_type, giver_name, quest_type in self.eligible_quests:
            quest = self.generate_quest(giver_type, giver_name, quest_type)
            if quest is not None:
                result[quest_type].append(quest)
        return result

    # ---- generation methods ----
    def _generate_AttackThreateningEntities(self, giver_type: str, giver_name: str) -> Optional[Dict[str, Any]]:
        locs = self.ws.get_all_locations_with_enemies()
        if not locs:
            return None
        location, enemies = random.choice(locs)
        enemy = random.choice(enemies)
        giver_loc = self.ws.get_npc_location(giver_name) if giver_type == "npc" else "unknown"
        atomic_actions = [
            ("goto", location),
            ("damage", enemy),
            ("goto", giver_loc),
            ("report", giver_name)
        ]
        return {
            "giver": {"type": giver_type, "name": giver_name},
            "type": "AttackThreateningEntities",
            "target": {"type": "enemy", "name": enemy, "location": location},
            "steps": atomic_actions
        }

    def _generate_RecoverStolenItem(self, giver_type: str, giver_name: str) -> Optional[Dict[str, Any]]:
        items = self.ws.get_giver_items(giver_type, giver_name)
        if not items:
            return None
        item = random.choice(items)
        # Find any non‑friendly entity (NPC or Faction)
        enemies = self.ws.get_non_friendly_entities(giver_type, giver_name)
        if not enemies:
            return None
        thief_type, thief_name = random.choice(enemies)
        # Determine thief location
        if thief_type == "npc":
            thief_loc = self.ws.get_npc_location(thief_name)
        else:
            thief_loc = self.ws.get_faction_location(thief_name)
        giver_loc = self.ws.get_npc_location(giver_name) if giver_type == "npc" else "unknown"
        atomic_actions = [
            ("goto", thief_loc),
            ("stealth", thief_name),
            ("take", item),
            ("goto", giver_loc),
            ("give", item, giver_name)
        ]
        return {
            "giver": {"type": giver_type, "name": giver_name},
            "type": "RecoverStolenItem",
            "target": {"type": "item", "name": item, "thief": {"type": thief_type, "name": thief_name}},
            "steps": atomic_actions
        }

    def _generate_GuardEntity(self, giver_type: str, giver_name: str) -> Optional[Dict[str, Any]]:
        if giver_type != "faction":
            return None
        members = self.ws.get_faction_members(giver_name)
        if not members:
            for friend in self.ws.get_friendly_factions(giver_name):
                members.extend(self.ws.get_faction_members(friend))
        if not members:
            return None
        target_npc = random.choice(members)
        target_loc = self.ws.get_npc_location(target_npc)
        atomic_actions = [
            ("goto", target_loc),
            ("defend", target_npc)
        ]
        return {
            "giver": {"type": giver_type, "name": giver_name},
            "type": "GuardEntity",
            "target": {"type": "npc", "name": target_npc, "location": target_loc},
            "steps": atomic_actions
        }

    def _generate_AttackEnemy(self, giver_type: str, giver_name: str) -> Optional[Dict[str, Any]]:
        # Enemies can be NPCs or Factions
        npc_enemies = self.ws.get_npcs_with_negative_relation(giver_type, giver_name)
        faction_enemies = self.ws.get_factions_with_negative_relation(giver_type, giver_name)
        if not npc_enemies and not faction_enemies:
            return None
        # Choose randomly between NPC and faction enemies
        enemies = [("npc", e) for e in npc_enemies] + [("faction", e) for e in faction_enemies]
        target_type, target_name = random.choice(enemies)
        # Determine location
        if target_type == "npc":
            target_loc = self.ws.get_npc_location(target_name)
        else:
            target_loc = self.ws.get_faction_location(target_name)
        atomic_actions = [
            ("goto", target_loc),
            ("damage", target_name)
        ]
        return {
            "giver": {"type": giver_type, "name": giver_name},
            "type": "AttackEnemy",
            "target": {"type": target_type, "name": target_name, "location": target_loc},
            "steps": atomic_actions
        }


    def _generate_StealStuff(self, giver_type: str, giver_name: str) -> Optional[Dict[str, Any]]:
        # Victims can be NPCs or Factions that giver dislikes
        npc_victims = self.ws.get_npcs_with_negative_relation(giver_type, giver_name)
        faction_victims = self.ws.get_factions_with_negative_relation(giver_type, giver_name)
        if not npc_victims and not faction_victims:
            return None
        # Shuffle and find one that has at least one item
        victims = [("npc", v) for v in npc_victims] + [("faction", v) for v in faction_victims]
        random.shuffle(victims)
        victim_type, victim_name = None, None
        victim_item = None
        for vt, vn in victims:
            items = self.ws.get_giver_items(vt, vn)
            if items:
                victim_type, victim_name = vt, vn
                victim_item = random.choice(items)
                break
        if not victim_type:
            return None
        # Determine location
        if victim_type == "npc":
            victim_loc = self.ws.get_npc_location(victim_name)
        else:
            victim_loc = self.ws.get_faction_location(victim_name)
        giver_loc = self.ws.get_npc_location(giver_name) if giver_type == "npc" else "unknown"
        atomic_actions = [
            ("goto", victim_loc),
            ("stealth", victim_name),
            ("take", victim_item),
            ("goto", giver_loc),
            ("give", victim_item, giver_name)
        ]
        return {
            "giver": {"type": giver_type, "name": giver_name},
            "type": "StealStuff",
            "target": {"type": "item", "name": victim_item, "victim": {"type": victim_type, "name": victim_name}},
            "steps": atomic_actions
        }

    def _generate_KillEnemies(self, giver_type: str, giver_name: str) -> Optional[Dict[str, Any]]:
        targets = self.ws.get_npcs_with_high_negative_relation(giver_type, giver_name, threshold=-3)
        if not targets:
            return None
        target = random.choice(targets)
        target_loc = self.ws.get_npc_location(target)
        giver_loc = self.ws.get_npc_location(giver_name) if giver_type == "npc" else "unknown"
        atomic_actions = [
            ("goto", target_loc),
            ("kill", target),
            ("goto", giver_loc),
            ("report", giver_name)
        ]
        return {
            "giver": {"type": giver_type, "name": giver_name},
            "type": "KillEnemies",
            "target": {"type": "npc", "name": target, "location": target_loc},
            "steps": atomic_actions
        }