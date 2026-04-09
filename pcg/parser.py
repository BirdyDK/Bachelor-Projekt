import re
import json
from typing import Dict, Any, List, Union

# Default relationship mapping (used if no custom mapping is provided)
DEFAULT_RELATION_MAP = {
    "Sworn Enemy": -50,
    "Enemy": -30,
    "Hated": -15,
    "Disliked": -5,
    "Neutral": 0,
    "Friendly": 5,
    "Friend": 15,
    "Ally": 30,
    "Sworn Ally": 50,
}

def convert_relation(value: Union[int, str], relation_map: Dict[str, int]) -> int:
    """Convert a relation value to an integer using the given map (case‑insensitive)."""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        # Normalise to title case for lookup (e.g., "sworn enemy" -> "Sworn Enemy")
        # First, try exact match
        if value in relation_map:
            return relation_map[value]
        # Try title case
        title_val = value.title()
        if title_val in relation_map:
            return relation_map[title_val]
        # Try uppercase lookup
        upper_val = value.upper()
        for k, v in relation_map.items():
            if k.upper() == upper_val:
                return v
        # Try to parse as integer
        try:
            return int(value)
        except ValueError:
            print(f"Warning: Unknown relation string '{value}', defaulting to 0")
            return 0
    return 0

def parse_world_data(filepath: str) -> Dict[str, Any]:
    """Parse the custom world_data.csv format into structured data."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    data = {
        "enums": {},
        "npcs": {},
        "factions": {},
        "enemies": {},
        "locations": {},
        "items": {},
        "player": {}
    }

    full_text = "".join(lines)
    enum_match = re.search(r'ENUM DATA\s*(\{.*?\})\s*;', full_text, re.DOTALL)
    if enum_match:
        try:
            data["enums"] = json.loads(enum_match.group(1))
        except:
            pass

    # Build relation mapping from enums if available
    relation_map = DEFAULT_RELATION_MAP.copy()
    # The spec expects a dict under Types.RelationshipLevels
    rel_levels = data["enums"].get("Types", {}).get("RelationshipLevels")
    if isinstance(rel_levels, dict):
        for k, v in rel_levels.items():
            relation_map[k] = int(v)
    elif isinstance(rel_levels, list):
        # Fallback for old format: map list indices to values? Not needed for new data.
        pass

    sections = re.split(r'^###? ', full_text, flags=re.MULTILINE)
    for section in sections:
        if not section.strip():
            continue
        if section.startswith("NPC DATA"):
            data["npcs"] = _parse_entity_dict(section, "NPC", relation_map)
        elif section.startswith("FACTION DATA"):
            data["factions"] = _parse_entity_dict(section, "FACTION", relation_map)
        elif section.startswith("ENEMY DATA"):
            data["enemies"] = _parse_entity_dict(section, "ENEMY", relation_map)
        elif section.startswith("LOCATION DATA"):
            data["locations"] = _parse_entity_dict(section, "LOCATION", relation_map)
        elif section.startswith("ITEM DATA"):
            data["items"] = _parse_entity_dict(section, "ITEM", relation_map)
        elif section.startswith("PLAYER DATA"):
            player_json = re.search(r'(\{.*\})', section, re.DOTALL)
            if player_json:
                try:
                    player_data = json.loads(player_json.group(1))
                    # Convert relation values in player data
                    for rel_list in ["FactionRelations", "NPCRelations"]:
                        if rel_list in player_data:
                            for rel in player_data[rel_list]:
                                if "Favorability" in rel:
                                    rel["Favorability"] = convert_relation(rel["Favorability"], relation_map)
                    data["player"] = player_data
                except:
                    pass
    return data

def _parse_entity_dict(block: str, entity_type: str, relation_map: Dict[str, int]) -> Dict[str, Any]:
    entities = {}
    lines = block.splitlines()
    content_lines = []
    header_passed = False
    for line in lines:
        if not header_passed:
            if line.strip().startswith(entity_type + " DATA"):
                header_passed = True
            continue
        content_lines.append(line)
    content = "\n".join(content_lines)

    pattern = r'^([A-Za-z][A-Za-z\s]+):\s*(\{.*?\n\})\s*(?=^[A-Za-z]|$)'
    matches = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
    for name, body in matches:
        name = name.strip()
        try:
            obj = json.loads(body)
            # Convert relations inside the entity
            if "Relations" in obj:
                for rel in obj["Relations"]:
                    if "Favorability" in rel:
                        rel["Favorability"] = convert_relation(rel["Favorability"], relation_map)
            entities[name] = obj
        except json.JSONDecodeError:
            # Try to fix missing quotes
            fixed = re.sub(r'(\w+):', r'"\1":', body)
            try:
                obj = json.loads(fixed)
                if "Relations" in obj:
                    for rel in obj["Relations"]:
                        if "Favorability" in rel:
                            rel["Favorability"] = convert_relation(rel["Favorability"], relation_map)
                entities[name] = obj
            except:
                print(f"Warning: Could not parse {name}")
                entities[name] = {}
    return entities