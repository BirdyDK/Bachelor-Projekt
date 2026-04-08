#!/usr/bin/env python3
"""
Generate a human‑readable display file for every row in quest_data.csv.
Output files are placed in quest_generator/display_output/output_<N>.txt
Each file includes a friendly summary followed by the raw JSON.
"""

import csv
import json
import os
import sys

def safe_extract_string(val):
    if isinstance(val, str):
        return val
    if isinstance(val, dict):
        if 'value' in val:
            return val['value']
        if '_value_' in val:
            return val['_value_']
    return str(val)

def build_lookup(world_dict):
    npc_names = {}
    npc_desc = {}
    for nid, data in world_dict.get("npcs", {}).items():
        name = data.get("name", nid)
        race = safe_extract_string(data.get("race", "unknown"))
        prof = safe_extract_string(data.get("profession", "unknown"))
        faction = data.get("faction", "unknown")
        npc_names[nid] = name
        npc_desc[nid] = f"[{faction} {race} {prof}] {name}"
    loc_names = {lid: data.get("name", lid) for lid, data in world_dict.get("locations", {}).items()}
    item_names = {iid: data.get("name", iid) for iid, data in world_dict.get("items", {}).items()}
    return npc_names, npc_desc, loc_names, item_names

def format_event(evt, npc_desc, item_names, npc_names):
    evt_type = safe_extract_string(evt.get("type", "unknown"))
    actor = evt.get("actor_id", "?")
    target = evt.get("target_id")
    item = evt.get("item_id")
    # We ignore the stored description and build everything from IDs

    actor_str = "player" if actor == "player" else npc_desc.get(actor, npc_names.get(actor, actor))
    # target could be an NPC id or a faction string
    target_str = ""
    if target:
        if target in npc_desc:
            target_str = npc_desc[target]
        elif target in npc_names:
            target_str = npc_names[target]
        else:
            target_str = target  # probably a faction name
    item_str = item_names.get(item, item) if item else ""

    if evt_type == "kill":
        return f"{actor_str} killed {target_str}"
    elif evt_type == "steal":
        return f"{actor_str} stole {item_str} from {target_str}"
    elif evt_type == "give":
        return f"{actor_str} gave {item_str} to {target_str}"
    elif evt_type == "help":
        return f"{actor_str} helped {target_str}"
    elif evt_type == "quest_given":
        return f"{actor_str} gave a quest to {target_str}"
    elif evt_type == "quest_completed":
        return f"{actor_str} completed a quest for {target_str}"
    elif evt_type == "gather":
        return f"{actor_str} gathered {item_str}"
    elif evt_type == "craft":
        return f"{actor_str} crafted {item_str}"
    elif evt_type == "fight":
        return f"{actor_str} fought {target_str}"
    elif evt_type == "alliance":
        return f"{actor_str} allied with {target_str}"
    elif evt_type == "conflict":
        return f"{actor_str} became enemies with {target_str}"
    elif evt_type == "trade":
        return f"{actor_str} traded with {target_str}"
    else:
        return f"{actor_str} performed {evt_type} on {target_str}"

def format_human_readable_summary(world_dict, player_dict, quest_dict):
    npc_names, npc_desc, loc_names, item_names = build_lookup(world_dict)

    lines = []
    lines.append("=" * 60)
    lines.append(" HUMAN‑READABLE SUMMARY")
    lines.append("=" * 60)

    loc_id = player_dict.get("current_location_id", "")
    loc_name = loc_names.get(loc_id, loc_id)
    lines.append(f"\n📍 Player is at: {loc_name}")

    inv = player_dict.get("inventory", [])
    if inv:
        items = [item_names.get(iid, iid) for iid in inv]
        lines.append(f"🎒 Inventory: {', '.join(items)}")
    else:
        lines.append("🎒 Inventory: (empty)")

    rep = player_dict.get("faction_reputation", {})
    if rep:
        lines.append("💬 Faction Reputation:")
        for faction, score in rep.items():
            lines.append(f"   {faction}: {score}")
    else:
        lines.append("💬 Faction Reputation: (none)")

    giver_id = quest_dict.get("giver_id", "")
    giver_desc = npc_desc.get(giver_id, npc_names.get(giver_id, giver_id))
    reason = quest_dict.get("reason", "")
    lines.append(f"\n📜 Quest from {giver_desc}")
    lines.append(f"   Reason: {reason}")

    action_log = player_dict.get("action_log", [])
    if action_log:
        lines.append("\n🕒 Recent player actions:")
        for evt in action_log[-5:]:
            lines.append(f"   • {format_event(evt, npc_desc, item_names, npc_names)}")
    else:
        lines.append("\n🕒 No player actions logged.")

    world_events = world_dict.get("events", [])
    if world_events:
        lines.append("\n🌍 World events:")
        for evt in world_events[-5:]:
            lines.append(f"   • {format_event(evt, npc_desc, item_names, npc_names)}")
    else:
        lines.append("\n🌍 No world events logged.")

    lines.append("")
    return "\n".join(lines)

def write_display_file(row_num: int, row_data, output_dir: str):
    world_json, player_json, atomic_json, quest_json, narrative = row_data

    try:
        world_dict = json.loads(world_json)
        player_dict = json.loads(player_json)
        quest_dict = json.loads(quest_json)
    except json.JSONDecodeError as e:
        print(f"Warning: Could not parse JSON in row {row_num}: {e}")
        world_dict, player_dict, quest_dict = {}, {}, {}

    summary = format_human_readable_summary(world_dict, player_dict, quest_dict)

    def format_section(title: str, content: str) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append(f" {title}")
        lines.append("=" * 60)
        lines.append(content)
        lines.append("")
        return "\n".join(lines)

    content_parts = [
        summary,
        format_section("WORLD STATE (JSON)", world_json),
        format_section("PLAYER STATE (JSON)", player_json),
        format_section("ATOMIC ACTIONS", atomic_json),
        format_section("QUEST STRUCTURE (JSON)", quest_json),
        format_section("NARRATIVE", narrative),
    ]

    filename = f"output_{row_num}.txt"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("\n".join(content_parts))

def main():
    csv_path = os.path.join("quest_generator", "quest_data.csv")
    output_dir = os.path.join("quest_generator", "display_output")

    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Run main.py first to generate data.")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, quoting=csv.QUOTE_ALL)
        header = next(reader)
        rows = list(reader)

    print(f"Generating {len(rows)} display files in {output_dir} ...")
    for idx, row in enumerate(rows, start=1):
        write_display_file(idx, row, output_dir)
        if idx % 10 == 0:
            print(f"  Processed {idx} rows")

    print("Done.")

if __name__ == "__main__":
    main()