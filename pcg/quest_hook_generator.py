import json
import os
import random
from typing import Dict, Any, List

class QuestHookGenerator:
    def __init__(self, templates_file: str = None):
        if templates_file is None:
            templates_file = os.path.join(os.path.dirname(__file__), "hook_templates.json")
        with open(templates_file, 'r', encoding='utf-8') as f:
            self.templates = json.load(f)
        # Load player name from generated quests or default
        self.player_name = "adventurer"  # will be updated from first quest's giver? Actually we need from world state.
        # We'll read it from the quest data if available, but for now keep placeholder.

    def set_player_name(self, name: str):
        self.player_name = name

    def generate_hook(self, quest: Dict[str, Any]) -> str:
        """Create a natural language quest hook from the quest data."""
        qtype = quest["type"]
        giver = quest["giver"]
        giver_name = giver["name"]
        giver_type = giver["type"]
        target = quest.get("target", {})
        steps = quest.get("steps", [])

        # Try to get giver's role and species from the original world data?
        # Since we don't have world state here, we'll rely on data embedded in quest or use defaults.
        # For better hooks, we could pass world state, but we keep minimal.
        giver_role = "person"
        giver_species = ""
        # If we had extra fields in quest, we could use them. We'll add simple defaults.

        # Determine relation tone (positive/negative) from giver type? Not stored, so we skip.

        # Prepare placeholders
        placeholders = {
            "giver_name": giver_name,
            "giver_role": giver_role,
            "giver_species": giver_species,
            "player_name": self.player_name,
            "location": target.get("location", "unknown"),
            "item": target.get("name", "something"),
            "target_name": target.get("name", "someone"),
            "target_type": target.get("type", "entity"),
            "enemies": target.get("name", "enemies"),
            "thief_name": target.get("thief", {}).get("name", "a thief") if isinstance(target.get("thief"), dict) else target.get("thief", "a thief"),
            "victim_name": target.get("victim", {}).get("name", "someone") if isinstance(target.get("victim"), dict) else target.get("victim", "someone"),
        }

        # Get template group for this quest type
        q_templates = self.templates.get(qtype, {})
        # Fallback to generic
        generic = self.templates.get("generic", {})

        # Build hook sentence by sentence
        parts = []

        # Greeting
        greeting = random.choice(generic.get("greetings", ["Listen up."]))
        parts.append(greeting.format(**placeholders))

        # Relation‑specific line (if we had relation, we could choose)
        # We'll skip for now, but can be added later.

        # Opener specific to quest type
        openers = q_templates.get("openers", [])
        if openers:
            parts.append(random.choice(openers).format(**placeholders))

        # Reason (optional)
        reasons = q_templates.get("reason", [])
        if reasons and random.random() < 0.7:  # 70% chance to include a reason
            parts.append(random.choice(reasons).format(**placeholders))

        # Additional info (e.g., thief for recover, victim for steal)
        if qtype == "RecoverStolenItem":
            thief_info = q_templates.get("thief_info", [])
            if thief_info:
                parts.append(random.choice(thief_info).format(**placeholders))
        elif qtype == "StealStuff":
            target_info = q_templates.get("target_info", [])
            if target_info:
                parts.append(random.choice(target_info).format(**placeholders))
        elif qtype == "AttackEnemy" or qtype == "KillEnemies":
            target_info = q_templates.get("target_info", [])
            if target_info:
                parts.append(random.choice(target_info).format(**placeholders))

        # The ask (what the player must do)
        ask = q_templates.get("ask", ["Get it done."])
        parts.append(random.choice(ask).format(**placeholders))

        # Closing
        closing = random.choice(generic.get("closings", ["What do you say?"]))
        parts.append(closing.format(**placeholders))

        # Join into a paragraph
        hook = " ".join(parts)
        return hook

    def add_hooks_to_quests(self, quests_by_type: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Return a copy of the quest dictionary with a 'hook' field added to each quest."""
        result = {}
        for qtype, quest_list in quests_by_type.items():
            result[qtype] = []
            for quest in quest_list:
                new_quest = quest.copy()
                new_quest["hook"] = self.generate_hook(quest)
                result[qtype].append(new_quest)
        return result

    def process_file(self, input_file: str, output_file: str):
        """Read quests from input JSON, add hooks, write to output JSON."""
        with open(input_file, 'r', encoding='utf-8') as f:
            quests_by_type = json.load(f)
        # Try to extract player name from any quest's giver? Not stored. Use default or read from world state.
        # We'll just use a default.
        self.player_name = "Kaelen"  # could be read from world_data.csv, but to keep separate, hardcode or pass.
        hooked = self.add_hooks_to_quests(quests_by_type)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(hooked, f, indent=2, ensure_ascii=False)
        print(f"Hooks added. Saved to {output_file}")

if __name__ == "__main__":
    # Standalone execution: read generated_quests.json, write generated_quests_with_hooks.json
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, "generated_quests.json")
    output_path = os.path.join(script_dir, "generated_quests_with_hooks.json")
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found. Run pcg/__main__.py first.")
    else:
        generator = QuestHookGenerator()
        # Optionally read player name from world_data.csv (we'll skip to keep minimal)
        generator.player_name = "Kaelen"  # from original data
        generator.process_file(input_path, output_path)