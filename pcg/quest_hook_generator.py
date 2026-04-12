import json
import os
import random
from typing import Dict, Any, List, Optional
from .world_state import WorldState

class QuestHookGenerator:
    def __init__(self, world_state: WorldState, templates_file: str = None):
        self.ws = world_state
        if templates_file is None:
            templates_file = os.path.join(os.path.dirname(__file__), "hook_templates.json")
        with open(templates_file, 'r', encoding='utf-8') as f:
            self.templates = json.load(f)
        self.player_name = self.ws.player_name

    def _get_entity_properties(self, entity_type: str, entity_name: str) -> Dict[str, str]:
        props = {}
        if entity_type == "npc":
            data = self.ws.npcs.get(entity_name, {})
            props["name"] = entity_name
            props["name_possessive"] = data.get("NamePossessive", f"{entity_name}'s")
            # For NPCs, definitive form is just the name (no article)
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

    def generate_hook(self, quest: Dict[str, Any]) -> str:
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

    def add_hooks_to_quests(self, quests_by_type: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        result = {}
        for qtype, quest_list in quests_by_type.items():
            result[qtype] = []
            for quest in quest_list:
                new_quest = quest.copy()
                new_quest["hook"] = self.generate_hook(quest)
                result[qtype].append(new_quest)
        return result