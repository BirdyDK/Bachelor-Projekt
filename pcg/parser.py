import re
import json
from typing import Dict, Any, List

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

    sections = re.split(r'^###? ', full_text, flags=re.MULTILINE)
    for section in sections:
        if not section.strip():
            continue
        if section.startswith("NPC DATA"):
            data["npcs"] = _parse_entity_dict(section, "NPC")
        elif section.startswith("FACTION DATA"):
            data["factions"] = _parse_entity_dict(section, "FACTION")
        elif section.startswith("ENEMY DATA"):
            data["enemies"] = _parse_entity_dict(section, "ENEMY")
        elif section.startswith("LOCATION DATA"):
            data["locations"] = _parse_entity_dict(section, "LOCATION")
        elif section.startswith("ITEM DATA"):
            data["items"] = _parse_entity_dict(section, "ITEM")
        elif section.startswith("PLAYER DATA"):
            player_json = re.search(r'(\{.*\})', section, re.DOTALL)
            if player_json:
                try:
                    data["player"] = json.loads(player_json.group(1))
                except:
                    pass
    return data

def _parse_entity_dict(block: str, entity_type: str) -> Dict[str, Any]:
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
            entities[name] = obj
        except json.JSONDecodeError:
            fixed = re.sub(r'(\w+):', r'"\1":', body)
            try:
                entities[name] = json.loads(fixed)
            except:
                print(f"Warning: Could not parse {name}")
                entities[name] = {}
    return entities