import random
from typing import Dict, Any, List, Optional, Tuple
from world_state import WorldState

class QuestGenerator:
    def __init__(self, world_state: WorldState, debug: bool = False):
        self.ws = world_state
        self.eligible_quests = []
        self.debug = debug

    def log(self, msg: str):
        if self.debug:
            print(f"[DEBUG] {msg}")

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
            self.log(f"Attempting {quest_type} from {giver_type} {giver_name}")
            result = getattr(self, method_name)(giver_type, giver_name)
            if result is None:
                self.log(f"  -> FAILED: {quest_type} from {giver_type} {giver_name}")
            return result
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

    # ---------- Helper for rewards and favorability ----------
    def _generate_reward_and_favorability(self, quest_type: str, giver_type: str, giver_name: str,
                                          target_info: Dict[str, Any]) -> Tuple[Dict[str, int], Dict[str, int]]:
        """Return (received, favorability) for the quest."""
        received = {}
        favorability = {}

        # Base favorability change from giver (positive if relation was good, but always positive for completing)
        # In a real system, this would depend on quest difficulty, but we'll use simple values.
        base_favor = 1
        if quest_type == "KillEnemies":
            base_favor = 2
        elif quest_type == "StealStuff":
            base_favor = 1
        elif quest_type == "RecoverStolenItem":
            base_favor = 2
        elif quest_type == "GuardEntity":
            base_favor = 1
        elif quest_type == "AttackEnemy":
            base_favor = 1
        elif quest_type == "AttackThreateningEntities":
            base_favor = 1

        # Giver gains favor
        favorability[giver_name] = favorability.get(giver_name, 0) + base_favor

        # Target (if NPC or faction) loses favor (negative effect)
        target_name = target_info.get("name")
        target_type = target_info.get("type")
        if target_type in ("npc", "faction") and target_name:
            favorability[target_name] = favorability.get(target_name, 0) - base_favor

        # Determine rewards based on quest type
        if quest_type == "AttackThreateningEntities":
            # Reward: loot from the enemy (random item)
            enemy_name = target_info.get("name")
            enemy_data = self.ws.enemies.get(enemy_name, {})
            loot_table = enemy_data.get("Loot", [])
            if loot_table:
                item = random.choice(loot_table)
                received[item] = random.randint(1, 3)
            else:
                received["Gold Coin"] = random.randint(10, 50)

        elif quest_type == "RecoverStolenItem":
            # Reward: some gold or a small item from the giver's treasury
            if giver_type == "npc":
                # NPCs might give a small item
                items = self.ws.get_giver_items(giver_type, giver_name)
                if items:
                    item = random.choice(items)
                    received[item] = 1
                else:
                    received["Gold Coin"] = random.randint(20, 60)
            else:
                # Faction gives gold from treasury
                received["Gold Coin"] = random.randint(50, 150)

        elif quest_type == "GuardEntity":
            received["Gold Coin"] = random.randint(30, 100)

        elif quest_type == "AttackEnemy":
            received["Gold Coin"] = random.randint(40, 120)

        elif quest_type == "StealStuff":
            # Reward: part of the stolen item or gold
            stolen_item = target_info.get("name")
            if stolen_item:
                received[stolen_item] = 1
            else:
                received["Gold Coin"] = random.randint(25, 75)

        elif quest_type == "KillEnemies":
            received["Gold Coin"] = random.randint(100, 300)
            # chance of rare item
            if random.random() < 0.3:
                received["Ancient Artifact"] = 1

        return received, favorability

    # ---------- Quest generation methods ----------
    def _generate_AttackThreateningEntities(self, giver_type: str, giver_name: str) -> Optional[Dict[str, Any]]:
        locs = self.ws.get_all_locations_with_enemies()
        if not locs:
            return None
        location, enemies = random.choice(locs)
        enemy = random.choice(enemies)
        if giver_type == "npc":
            giver_loc = self.ws.get_npc_location(giver_name)
        else:
            giver_loc = self.ws.get_faction_location(giver_name)
        atomic_actions = [
            ("goto", location),
            ("damage", enemy),
            ("goto", giver_loc),
            ("report", giver_name)
        ]
        target_info = {"type": "enemy", "name": enemy, "location": location}
        received, favorability = self._generate_reward_and_favorability(
            "AttackThreateningEntities", giver_type, giver_name, target_info
        )
        return {
            "giver": {"type": giver_type, "name": giver_name},
            "type": "AttackThreateningEntities",
            "target": target_info,
            "steps": atomic_actions,
            "received": received,
            "favorability": favorability
        }

    def _generate_RecoverStolenItem(self, giver_type: str, giver_name: str) -> Optional[Dict[str, Any]]:
        items = self.ws.get_giver_items(giver_type, giver_name)
        if not items:
            return None
        item = random.choice(items)
        enemies = self.ws.get_non_friendly_entities(giver_type, giver_name)
        if not enemies:
            return None
        thief_type, thief_name = random.choice(enemies)
        if thief_type == "npc":
            thief_loc = self.ws.get_npc_location(thief_name)
        else:
            thief_loc = self.ws.get_faction_location(thief_name)
        if giver_type == "npc":
            giver_loc = self.ws.get_npc_location(giver_name)
        else:
            giver_loc = self.ws.get_faction_location(giver_name)
        atomic_actions = [
            ("goto", thief_loc),
            ("stealth", thief_name),
            ("take", item),
            ("goto", giver_loc),
            ("give", item, giver_name)
        ]
        target_info = {"type": "item", "name": item, "thief": {"type": thief_type, "name": thief_name}}
        received, favorability = self._generate_reward_and_favorability(
            "RecoverStolenItem", giver_type, giver_name, target_info
        )
        return {
            "giver": {"type": giver_type, "name": giver_name},
            "type": "RecoverStolenItem",
            "target": target_info,
            "steps": atomic_actions,
            "received": received,
            "favorability": favorability
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
        target_info = {"type": "npc", "name": target_npc, "location": target_loc}
        received, favorability = self._generate_reward_and_favorability(
            "GuardEntity", giver_type, giver_name, target_info
        )
        return {
            "giver": {"type": giver_type, "name": giver_name},
            "type": "GuardEntity",
            "target": target_info,
            "steps": atomic_actions,
            "received": received,
            "favorability": favorability
        }

    def _generate_AttackEnemy(self, giver_type: str, giver_name: str) -> Optional[Dict[str, Any]]:
        npc_enemies = self.ws.get_npcs_with_negative_relation(giver_type, giver_name)
        faction_enemies = self.ws.get_factions_with_negative_relation(giver_type, giver_name)
        if not npc_enemies and not faction_enemies:
            return None
        enemies = [("npc", e) for e in npc_enemies] + [("faction", e) for e in faction_enemies]
        target_type, target_name = random.choice(enemies)
        if target_type == "npc":
            target_loc = self.ws.get_npc_location(target_name)
        else:
            target_loc = self.ws.get_faction_location(target_name)
        atomic_actions = [
            ("goto", target_loc),
            ("damage", target_name)
        ]
        target_info = {"type": target_type, "name": target_name, "location": target_loc}
        received, favorability = self._generate_reward_and_favorability(
            "AttackEnemy", giver_type, giver_name, target_info
        )
        return {
            "giver": {"type": giver_type, "name": giver_name},
            "type": "AttackEnemy",
            "target": target_info,
            "steps": atomic_actions,
            "received": received,
            "favorability": favorability
        }

    def _generate_StealStuff(self, giver_type: str, giver_name: str) -> Optional[Dict[str, Any]]:
        npc_victims = self.ws.get_npcs_with_negative_relation(giver_type, giver_name)
        faction_victims = self.ws.get_factions_with_negative_relation(giver_type, giver_name)
        if not npc_victims and not faction_victims:
            return None
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
        if victim_type == "npc":
            victim_loc = self.ws.get_npc_location(victim_name)
        else:
            victim_loc = self.ws.get_faction_location(victim_name)
        if giver_type == "npc":
            giver_loc = self.ws.get_npc_location(giver_name)
        else:
            giver_loc = self.ws.get_faction_location(giver_name)
        atomic_actions = [
            ("goto", victim_loc),
            ("stealth", victim_name),
            ("take", victim_item),
            ("goto", giver_loc),
            ("give", victim_item, giver_name)
        ]
        target_info = {"type": "item", "name": victim_item, "victim": {"type": victim_type, "name": victim_name}}
        received, favorability = self._generate_reward_and_favorability(
            "StealStuff", giver_type, giver_name, target_info
        )
        return {
            "giver": {"type": giver_type, "name": giver_name},
            "type": "StealStuff",
            "target": target_info,
            "steps": atomic_actions,
            "received": received,
            "favorability": favorability
        }

    def _generate_KillEnemies(self, giver_type: str, giver_name: str) -> Optional[Dict[str, Any]]:
        npc_targets = self.ws.get_npcs_with_high_negative_relation(giver_type, giver_name, threshold=-3)
        if npc_targets:
            target = random.choice(npc_targets)
            target_type = "npc"
            target_loc = self.ws.get_npc_location(target)
        else:
            faction_targets = self.ws.get_factions_with_negative_relation(giver_type, giver_name)
            strong_factions = []
            for ft in faction_targets:
                rel = self.ws.get_relation(giver_type, giver_name, ft)
                if rel <= -3:
                    strong_factions.append(ft)
            if not strong_factions:
                return None
            target_faction = random.choice(strong_factions)
            members = self.ws.get_faction_members(target_faction)
            if not members:
                return None
            target = random.choice(members)
            target_type = "npc"
            target_loc = self.ws.get_npc_location(target)
        if giver_type == "npc":
            giver_loc = self.ws.get_npc_location(giver_name)
        else:
            giver_loc = self.ws.get_faction_location(giver_name)
        atomic_actions = [
            ("goto", target_loc),
            ("kill", target),
            ("goto", giver_loc),
            ("report", giver_name)
        ]
        target_info = {"type": target_type, "name": target, "location": target_loc}
        received, favorability = self._generate_reward_and_favorability(
            "KillEnemies", giver_type, giver_name, target_info
        )
        return {
            "giver": {"type": giver_type, "name": giver_name},
            "type": "KillEnemies",
            "target": target_info,
            "steps": atomic_actions,
            "received": received,
            "favorability": favorability
        }