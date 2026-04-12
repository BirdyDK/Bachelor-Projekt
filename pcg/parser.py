import re
import json
from typing import Dict, Any, List, Union

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
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        if value in relation_map:
            return relation_map[value]
        title_val = value.title()
        if title_val in relation_map:
            return relation_map[title_val]
        upper_val = value.upper()
        for k, v in relation_map.items():
            if k.upper() == upper_val:
                return v
        try:
            return int(value)
        except ValueError:
            print(f"Warning: Unknown relation string '{value}', defaulting to 0")
            return 0
    return 0

def parse_world_data(filepath: str) -> Dict[str, Any]:
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

    relation_map = DEFAULT_RELATION_MAP.copy()
    rel_levels = data["enums"].get("Types", {}).get("RelationshipLevels")
    if isinstance(rel_levels, dict):
        for k, v in rel_levels.items():
            relation_map[k] = int(v)

    # Split into sections by lines starting with ### or ## (the delimiter is removed)
    sections = re.split(r'^###? ', full_text, flags=re.MULTILINE)
    for section in sections:
        if not section.strip():
            continue
        lines = section.splitlines()
        if not lines:
            continue
        header_line = lines[0].strip()
        content = "\n".join(lines[1:]) if len(lines) > 1 else ""
        if header_line.startswith("NPC DATA"):
            data["npcs"] = _parse_entity_dict(content, relation_map)
        elif header_line.startswith("FACTION DATA"):
            data["factions"] = _parse_entity_dict(content, relation_map)
        elif header_line.startswith("ENEMY DATA"):
            data["enemies"] = _parse_entity_dict(content, relation_map)
        elif header_line.startswith("LOCATION DATA"):
            data["locations"] = _parse_entity_dict(content, relation_map)
        elif header_line.startswith("ITEM DATA"):
            data["items"] = _parse_entity_dict(content, relation_map)
        elif header_line.startswith("PLAYER DATA"):
            player_json = re.search(r'(\{.*\})', content, re.DOTALL)
            if player_json:
                try:
                    player_data = json.loads(player_json.group(1))
                    for rel_list in ["FactionRelations", "NPCRelations"]:
                        if rel_list in player_data:
                            for rel in player_data[rel_list]:
                                if "Favorability" in rel:
                                    rel["Favorability"] = convert_relation(rel["Favorability"], relation_map)
                    data["player"] = player_data
                except:
                    pass
    return data

def _parse_entity_dict(content: str, relation_map: Dict[str, int]) -> Dict[str, Any]:
    """Parse a block containing multiple entity definitions (multi-line JSON allowed)."""
    entities = {}
    # Pattern matches "Name: { ... }" where the JSON can span multiple lines.
    # The pattern uses a non-greedy match for the JSON body, ending with a newline and then either another name or end of string.
    pattern = r'^([A-Za-z][A-Za-z\s]+):\s*(\{.*?\n\})\s*(?=^[A-Za-z]|$)'
    matches = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
    for name, body in matches:
        name = name.strip()
        try:
            obj = json.loads(body)
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