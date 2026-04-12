#!/usr/bin/env python3
"""
Procedural Quest Generator – Main entry point.
Place this file in the project root (next to the `pcg/` folder).
"""

import sys
import os
import json
import random
import argparse

# Add current directory to path so pcg package can be found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pcg.parser as world_parser
import pcg.world_state as world_state
import pcg.quest_generator as quest_generator
import pcg.quest_hook_generator as quest_hook_generator

# Default world data file (inside pcg/world_data folder)
DEFAULT_WORLD_FILE = "template_world_data.csv"

def get_world_data_file(base_dir: str, user_arg: str = None) -> str:
    world_data_dir = os.path.join(base_dir, "pcg", "world_data")
    if not os.path.exists(world_data_dir):
        print(f"Error: {world_data_dir} folder not found.")
        sys.exit(1)

    if user_arg:
        if os.path.isfile(user_arg):
            return user_arg
        candidate = os.path.join(world_data_dir, user_arg)
        if os.path.isfile(candidate):
            return candidate
        print(f"Error: Could not find file '{user_arg}' (tried as absolute/relative and inside {world_data_dir})")
        sys.exit(1)
    else:
        default_path = os.path.join(world_data_dir, DEFAULT_WORLD_FILE)
        if os.path.isfile(default_path):
            return default_path
        csv_files = [f for f in os.listdir(world_data_dir) if f.endswith('.csv')]
        if not csv_files:
            print(f"Error: No .csv files found in {world_data_dir} and default '{DEFAULT_WORLD_FILE}' missing.")
            sys.exit(1)
        chosen = random.choice(csv_files)
        return os.path.join(world_data_dir, chosen)

def ensure_output_dir(base_dir: str) -> str:
    output_dir = os.path.join(base_dir, "pcg", "output")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def load_world(data_file: str) -> world_state.WorldState:
    """Parse world data and return WorldState object."""
    print(f"Loading world data from: {os.path.basename(data_file)}")
    raw_data = world_parser.parse_world_data(data_file)
    world = world_state.WorldState(raw_data)
    return world

def generate_and_save(world: world_state.WorldState, script_dir: str, data_filename: str):
    """Run quest generation and save outputs."""
    print("Initializing quest generator...")
    generator = quest_generator.QuestGenerator(world)
    generator.compute_eligible_quests()

    eligible_counts = {}
    for _, _, qt in generator.eligible_quests:
        eligible_counts[qt] = eligible_counts.get(qt, 0) + 1

    print(f"Found {len(generator.eligible_quests)} relation‑eligible quests.")
    print("Eligible by relation:")
    for qt in ["AttackThreateningEntities", "RecoverStolenItem", "GuardEntity", "AttackEnemy", "StealStuff", "KillEnemies"]:
        print(f"  {qt}: {eligible_counts.get(qt, 0)}")

    print("\nGenerating all possible quests (with target checks)...")
    all_quests_by_type = generator.generate_all_quests()

    output_dir = ensure_output_dir(script_dir)
    output_file = os.path.join(output_dir, "generated_quests.json")
    output_data = {
        "world_data_source": data_filename,
        "quests": all_quests_by_type
    }
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"Generated quests saved to {output_file}")
    print("\nActual generated quests (after target availability):")
    for qtype, quests in all_quests_by_type.items():
        print(f"  {qtype}: {len(quests)} quests")

    print("\nGenerating quest hooks...")
    hook_gen = quest_hook_generator.QuestHookGenerator(world)
    hooked_quests = hook_gen.add_hooks_to_quests(all_quests_by_type)
    hooked_output_file = os.path.join(output_dir, "generated_quests_with_hooks.json")
    hooked_output_data = {
        "world_data_source": data_filename,
        "quests": hooked_quests
    }
    with open(hooked_output_file, 'w', encoding='utf-8') as f:
        json.dump(hooked_output_data, f, indent=2, ensure_ascii=False)
    print(f"Quests with hooks saved to {hooked_output_file}")

def interactive_mode(initial_world_file: str, script_dir: str):
    """Run interactive command loop."""
    current_file = initial_world_file
    world = load_world(current_file)
    print("\nInteractive mode active. Commands (case‑insensitive):")
    print("  LD <filename>  – Load a different world data file")
    print("  GQ PCG         – Generate quests and save to pcg/output/")
    print("  EXIT / QUIT    – Exit the program")
    print()

    while True:
        try:
            cmd = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if not cmd:
            continue
        if cmd in ("exit", "quit"):
            print("Goodbye!")
            break
        elif cmd.startswith("ld "):
            new_file_arg = cmd[3:].strip()
            if not new_file_arg:
                print("Usage: LD <filename>")
                continue
            world_data_dir = os.path.join(script_dir, "pcg", "world_data")
            if os.path.isfile(new_file_arg):
                new_path = new_file_arg
            else:
                new_path = os.path.join(world_data_dir, new_file_arg)
                if not os.path.isfile(new_path):
                    print(f"Error: Could not find file '{new_file_arg}'")
                    continue
            try:
                world = load_world(new_path)
                current_file = new_path
                print(f"Switched to world data: {os.path.basename(current_file)}")
            except Exception as e:
                print(f"Failed to load world data: {e}")
        elif cmd == "gq pcg":
            data_filename = os.path.basename(current_file)
            generate_and_save(world, script_dir, data_filename)
        else:
            print("Unknown command. Available: LD <file>, GQ PCG, EXIT")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    arg_parser = argparse.ArgumentParser(description='Procedural Quest Generator')
    arg_parser.add_argument('--world_data_file', type=str,
                            help='Specify a world data CSV file (filename in pcg/world_data/ folder or full path)')
    arg_parser.add_argument('--gq_pcg', action='store_true',
                            help='Automatically generate quests and exit (non‑interactive mode)')
    args = arg_parser.parse_args()

    if args.world_data_file:
        data_file = get_world_data_file(script_dir, args.world_data_file)
    else:
        data_file = get_world_data_file(script_dir, None)

    if args.gq_pcg:
        print(f"Using world data file: {os.path.basename(data_file)}")
        world = load_world(data_file)
        generate_and_save(world, script_dir, os.path.basename(data_file))
    else:
        interactive_mode(data_file, script_dir)

if __name__ == "__main__":
    main()