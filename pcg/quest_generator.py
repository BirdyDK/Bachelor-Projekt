import random
import json
import os
from typing import Dict, Any, List, Optional, Tuple
from .world_state import WorldState

class QuestGenerator:
    def __init__(self, world_state: WorldState, debug: bool = False, templates_file: str = None):
        self.ws = world_state
        self.eligible_quests = []
        self.debug = debug
        self.player_name = self.ws.player_name
        
        # Load hook templates
        if templates_file is None:
            templates_file = os.path.join(os.path.dirname(__file__), "hook_templates.json")
        with open(templates_file, 'r', encoding='utf-8') as f:
            self.templates = json.load(f)

    def log(self, msg: str):
        if self.debug:
            print(f"[DEBUG] {msg}")

    # ---------- Hook generation helpers (merged from quest_hook_generator) ----------
    def _get_entity_properties(self, entity_type: str, entity_name: str) -> Dict[str, str]:
        props = {}
        if entity_type == "npc":
            data = self.ws.npcs.get(entity_name, {})
            props["name"] = entity_name
            props["name_possessive"] = data.get("NamePossessive", f"{entity_name}'s")
            props["name_definitive"] = entity_name
            props["name_definitive_caps"] = entity_name
            props["name_definitive_possessive"] = data.get("NamePossessive", f"{entity_name}'s")
            props["name_definitive_possessive_caps"] = data.get("NamePossessive", f"{entity_name}'s")
            props["species"] = data.get("Species", "person")
            props["role"] = data.get("Role", "person")
        elif entity_type == "faction":
            data = self.ws.factions.get(entity_name, {})
            props["name"] = entity_name
            props["name_definitive"] = data.get("NameDefinitive", entity_name)
            props["name_definitive_caps"] = data.get("NameDefinitiveCaps", props["name_definitive"])
            props["name_possessive"] = data.get("NamePossessive", f"{entity_name}'s")
            props["name_definitive_possessive"] = data.get("NameDefinitivePossessive", f"the {entity_name}'s")
            props["name_definitive_possessive_caps"] = data.get("NameDefinitivePossessiveCaps", props["name_definitive_possessive"])
        elif entity_type == "location":
            data = self.ws.locations.get(entity_name, {})
            props["name"] = entity_name
            props["name_definitive"] = data.get("NameDefinitive", entity_name)
            props["name_definitive_caps"] = data.get("NameDefinitiveCaps", props["name_definitive"])
            props["name_possessive"] = data.get("NamePossessive", f"{entity_name}'s")
            props["name_definitive_possessive"] = data.get("NameDefinitivePossessive", f"the {entity_name}'s")
            props["name_definitive_possessive_caps"] = data.get("NameDefinitivePossessiveCaps", props["name_definitive_possessive"])
        elif entity_type == "item":
            data = self.ws.items.get(entity_name, {})
            props["name"] = entity_name
            props["name_singular"] = data.get("NameSingular", entity_name)
            props["name_plural"] = data.get("NamePlural", f"{entity_name}s")
            props["name_possessive_singular"] = data.get("NamePossessiveSingular", f"{entity_name}'s")
            props["name_possessive_plural"] = data.get("NamePossessivePlural", f"{entity_name}s'")
            props["indefinite_article"] = data.get("IndefiniteArticle", "a")
            props["indefinite_article_caps"] = data.get("IndefiniteArticleCaps", "A")
        elif entity_type == "enemy":
            data = self.ws.enemies.get(entity_name, {})
            props["name"] = entity_name
            props["name_singular"] = data.get("NameSingular", entity_name)
            props["name_plural"] = data.get("NamePlural", f"{entity_name}s")
            props["name_possessive_singular"] = data.get("NamePossessiveSingular", f"{entity_name}'s")
            props["name_possessive_plural"] = data.get("NamePossessivePlural", f"{entity_name}s'")
            props["indefinite_article"] = data.get("IndefiniteArticle", "a")
            props["indefinite_article_caps"] = data.get("IndefiniteArticleCaps", "A")
        else:
            props["name"] = entity_name
            props["name_possessive"] = f"{entity_name}'s"
            props["name_definitive"] = entity_name
            props["name_definitive_caps"] = entity_name
            props["name_definitive_possessive"] = f"{entity_name}'s"
            props["name_definitive_possessive_caps"] = f"{entity_name}'s"
        return props

    def _generate_hook(self, quest: Dict[str, Any]) -> str:
        qtype = quest["type"]
        giver = quest["giver"]
        giver_type = giver["type"]
        giver_name = giver["name"]
        target = quest.get("target", {})

        giver_props = self._get_entity_properties(giver_type, giver_name)
        target_type = target.get("type", "")
        target_name = target.get("name", "")
        target_props = self._get_entity_properties(target_type, target_name) if target_name else {}

        thief = target.get("thief", {})
        thief_props = self._get_entity_properties(thief.get("type", ""), thief.get("name", "")) if thief else {}
        victim = target.get("victim", {})
        victim_props = self._get_entity_properties(victim.get("type", ""), victim.get("name", "")) if victim else {}

        location_name = target.get("location", "unknown")
        location_props = self._get_entity_properties("location", location_name) if location_name != "unknown" else {
            "name": location_name,
            "name_definitive": location_name,
            "name_definitive_caps": location_name,
            "name_possessive": f"{location_name}'s",
            "name_definitive_possessive": f"the {location_name}'s",
            "name_definitive_possessive_caps": f"The {location_name}'s"
        }

        placeholders = {
            "player_name": self.player_name,
            "player_name_possessive": f"{self.player_name}'s",
            "giver_name": giver_props.get("name", giver_name),
            "giver_name_definitive": giver_props.get("name_definitive", giver_name),
            "giver_name_definitive_caps": giver_props.get("name_definitive_caps", giver_name),
            "giver_name_possessive": giver_props.get("name_possessive", f"{giver_name}'s"),
            "giver_name_definitive_possessive": giver_props.get("name_definitive_possessive", f"the {giver_name}'s"),
            "giver_name_definitive_possessive_caps": giver_props.get("name_definitive_possessive_caps", f"The {giver_name}'s"),
            "giver_species": giver_props.get("species", "person"),
            "giver_role": giver_props.get("role", "person"),
            "giver_faction": self.ws.npcs.get(giver_name, {}).get("Faction", "unknown") if giver_type == "npc" else "",
            "target_name": target_props.get("name", target_name),
            "target_name_definitive": target_props.get("name_definitive", target_name),
            "target_name_definitive_caps": target_props.get("name_definitive_caps", target_name),
            "target_name_possessive": target_props.get("name_possessive", f"{target_name}'s"),
            "target_name_definitive_possessive": target_props.get("name_definitive_possessive", f"the {target_name}'s"),
            "target_name_definitive_possessive_caps": target_props.get("name_definitive_possessive_caps", f"The {target_name}'s"),
            "target_type": target_type,
            "enemy_name_singular": target_props.get("name_singular", target_name),
            "enemy_name_plural": target_props.get("name_plural", f"{target_name}s"),
            "enemy_indefinite_article": target_props.get("indefinite_article", "a"),
            "enemy_indefinite_article_caps": target_props.get("indefinite_article_caps", "A"),
            "item_name": target_props.get("name", target_name),
            "item_name_singular": target_props.get("name_singular", target_name),
            "item_name_plural": target_props.get("name_plural", f"{target_name}s"),
            "item_indefinite_article": target_props.get("indefinite_article", "a"),
            "item_indefinite_article_caps": target_props.get("indefinite_article_caps", "A"),
            "item_name_possessive_singular": target_props.get("name_possessive_singular", f"{target_name}'s"),
            "item_name_possessive_plural": target_props.get("name_possessive_plural", f"{target_name}s'"),
            "location_name": location_props.get("name", location_name),
            "location_name_definitive": location_props.get("name_definitive", location_name),
            "location_name_definitive_caps": location_props.get("name_definitive_caps", location_name),
            "location_name_possessive": location_props.get("name_possessive", f"{location_name}'s"),
            "location_name_definitive_possessive": location_props.get("name_definitive_possessive", f"the {location_name}'s"),
            "location_name_definitive_possessive_caps": location_props.get("name_definitive_possessive_caps", f"The {location_name}'s"),
            "thief_name": thief_props.get("name", "a thief"),
            "thief_name_definitive": thief_props.get("name_definitive", "a thief"),
            "thief_name_definitive_caps": thief_props.get("name_definitive_caps", "A Thief"),
            "thief_name_possessive": thief_props.get("name_possessive", "the thief's"),
            "thief_name_definitive_possessive": thief_props.get("name_definitive_possessive", "the thief's"),
            "thief_name_definitive_possessive_caps": thief_props.get("name_definitive_possessive_caps", "The thief's"),
            "thief_type": thief.get("type", ""),
            "victim_name": victim_props.get("name", "someone"),
            "victim_name_definitive": victim_props.get("name_definitive", "someone"),
            "victim_name_definitive_caps": victim_props.get("name_definitive_caps", "Someone"),
            "victim_name_possessive": victim_props.get("name_possessive", "someone's"),
            "victim_name_definitive_possessive": victim_props.get("name_definitive_possessive", "someone's"),
            "victim_name_definitive_possessive_caps": victim_props.get("name_definitive_possessive_caps", "Someone's"),
        }

        q_templates = self.templates.get(qtype, {})
        generic = self.templates.get("generic", {})
        categories = q_templates.get("categories", {})
        sequences = q_templates.get("sequences", [])
        optional = q_templates.get("optional_categories", [])

        if not sequences:
            return self._fallback_hook(quest, placeholders)

        sequence = random.choice(sequences)
        sentences = []
        for cat in sequence:
            if cat in optional and random.random() < 0.3:
                continue
            templates = categories.get(cat, generic.get(cat, []))
            if not templates:
                continue
            template = random.choice(templates)
            sentences.append(template.format(**placeholders))

        return " ".join(sentences)

    def _fallback_hook(self, quest: Dict[str, Any], placeholders: Dict[str, str]) -> str:
        qtype = quest["type"]
        q_templates = self.templates.get(qtype, {})
        generic = self.templates.get("generic", {})
        parts = []
        if "greeting" in generic:
            parts.append(random.choice(generic["greeting"]).format(**placeholders))
        openers = q_templates.get("openers", [])
        if openers:
            parts.append(random.choice(openers).format(**placeholders))
        reasons = q_templates.get("reason", [])
        if reasons and random.random() < 0.7:
            parts.append(random.choice(reasons).format(**placeholders))
        if qtype == "RecoverStolenItem":
            thief_info = q_templates.get("thief_info", [])
            if thief_info:
                parts.append(random.choice(thief_info).format(**placeholders))
        elif qtype == "StealStuff":
            target_info = q_templates.get("target_info", [])
            if target_info:
                parts.append(random.choice(target_info).format(**placeholders))
        elif qtype in ("AttackEnemy", "KillEnemies"):
            target_info = q_templates.get("target_info", [])
            if target_info:
                parts.append(random.choice(target_info).format(**placeholders))
        ask = q_templates.get("ask", ["Get it done."])
        parts.append(random.choice(ask).format(**placeholders))
        closing = generic.get("closing", ["What do you say?"])
        parts.append(random.choice(closing).format(**placeholders))
        return " ".join(parts)

    # ---------- Original quest generation logic (unchanged) ----------
    def compute_eligible_quests(self):
        """Compute eligible quests based on relationship thresholds."""
        self.eligible_quests = []
        for npc_name in self.ws.npcs:
            relation = self.ws.get_relation("npc", npc_name)
            if relation >= -15:
                self.eligible_quests.append(("npc", npc_name, "AttackThreateningEntities"))
            if relation >= 30:
                self.eligible_quests.append(("npc", npc_name, "RecoverStolenItem"))
            if relation >= 5:
                self.eligible_quests.append(("npc", npc_name, "AttackEnemy"))
            if relation >= 15:
                self.eligible_quests.append(("npc", npc_name, "StealStuff"))
            if relation >= 30 or relation <= -30:
                self.eligible_quests.append(("npc", npc_name, "KillEnemies"))

        for faction_name in self.ws.factions:
            relation = self.ws.get_relation("faction", faction_name)
            if relation >= -15:
                self.eligible_quests.append(("faction", faction_name, "AttackThreateningEntities"))
            if relation >= 30:
                self.eligible_quests.append(("faction", faction_name, "RecoverStolenItem"))
            if relation >= 15:
                self.eligible_quests.append(("faction", faction_name, "GuardEntity"))
            if relation >= 5:
                self.eligible_quests.append(("faction", faction_name, "AttackEnemy"))
            if relation >= 15:
                self.eligible_quests.append(("faction", faction_name, "StealStuff"))
            if relation >= 30 or relation <= -30:
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
        """Generate all eligible quests and add hooks directly."""
        if not self.eligible_quests:
            self.compute_eligible_quests()
        result = {qt: [] for qt in ["AttackThreateningEntities", "RecoverStolenItem", "GuardEntity",
                                    "AttackEnemy", "StealStuff", "KillEnemies"]}
        for giver_type, giver_name, quest_type in self.eligible_quests:
            quest = self.generate_quest(giver_type, giver_name, quest_type)
            if quest is not None:
                # Add hook directly
                quest["hook"] = self._generate_hook(quest)
                result[quest_type].append(quest)
        return result

    # ---------- Reward and favorability helper (unchanged) ----------
    def _generate_reward_and_favorability(self, quest_type: str, giver_type: str, giver_name: str,
                                          target_info: Dict[str, Any]) -> Tuple[Dict[str, int], Dict[str, int]]:
        received = {}
        favorability = {}

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

        favorability[giver_name] = favorability.get(giver_name, 0) + base_favor

        target_name = target_info.get("name")
        target_type = target_info.get("type")
        if target_type in ("npc", "faction") and target_name:
            favorability[target_name] = favorability.get(target_name, 0) - base_favor

        if quest_type == "AttackThreateningEntities":
            enemy_name = target_info.get("name")
            enemy_data = self.ws.enemies.get(enemy_name, {})
            loot_table = enemy_data.get("Loot", [])
            if loot_table:
                item = random.choice(loot_table)
                received[item] = random.randint(1, 3)
            else:
                received["Gold Coin"] = random.randint(10, 50)

        elif quest_type == "RecoverStolenItem":
            if giver_type == "npc":
                items = self.ws.get_giver_items(giver_type, giver_name)
                if items:
                    item = random.choice(items)
                    received[item] = 1
                else:
                    received["Gold Coin"] = random.randint(20, 60)
            else:
                received["Gold Coin"] = random.randint(50, 150)

        elif quest_type == "GuardEntity":
            received["Gold Coin"] = random.randint(30, 100)

        elif quest_type == "AttackEnemy":
            received["Gold Coin"] = random.randint(40, 120)

        elif quest_type == "StealStuff":
            stolen_item = target_info.get("name")
            if stolen_item:
                received[stolen_item] = 1
            else:
                received["Gold Coin"] = random.randint(25, 75)

        elif quest_type == "KillEnemies":
            received["Gold Coin"] = random.randint(100, 300)
            if random.random() < 0.3:
                received["Ancient Artifact"] = 1

        return received, favorability

    # ---------- Generation methods (unchanged) ----------
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
        npc_targets = self.ws.get_npcs_with_high_negative_relation(giver_type, giver_name, threshold=-30)
        if npc_targets:
            target = random.choice(npc_targets)
            target_type = "npc"
            target_loc = self.ws.get_npc_location(target)
        else:
            faction_targets = self.ws.get_factions_with_negative_relation(giver_type, giver_name)
            strong_factions = []
            for ft in faction_targets:
                rel = self.ws.get_relation(giver_type, giver_name, ft)
                if rel <= -30:
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