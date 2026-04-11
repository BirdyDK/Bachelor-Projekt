import sys
import os
import json
import random
import argparse
import parser as world_parser
import world_state
import quest_generator
import quest_hook_generator

def get_world_data_file(base_dir: str, user_arg: str = None) -> str:
    world_data_dir = os.path.join(base_dir, "world_data")
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
        csv_files = [f for f in os.listdir(world_data_dir) if f.endswith('.csv')]
        if not csv_files:
            print(f"Error: No .csv files found in {world_data_dir}")
            sys.exit(1)
        chosen = random.choice(csv_files)
        return os.path.join(world_data_dir, chosen)

def ensure_output_dir(base_dir: str) -> str:
    """Create output folder if it doesn't exist, return its path."""
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set up argument parser
    arg_parser = argparse.ArgumentParser(description='Procedural Quest Generator')
    arg_parser.add_argument('--world_data_file', type=str, help='Specify a world data CSV file (filename in world_data/ folder or full path)')
    args = arg_parser.parse_args()
    
    # 1. Get the world data file
    data_file = get_world_data_file(script_dir, args.world_data_file)
    data_filename = os.path.basename(data_file)
    print(f"Using world data file: {data_filename} (full path: {data_file})")
    
    # 2. Parse it
    print("Parsing world data...")
    raw_data = world_parser.parse_world_data(data_file)
    world = world_state.WorldState(raw_data)
    
    # 3. Generate quests
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
    
    # 4. Save generated quests (with source filename) to output folder
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
    
    # 5. Generate hooks and save with source filename to output folder
    print("\nGenerating quest hooks...")
    hook_gen = quest_hook_generator.QuestHookGenerator(world)   # pass world object
    hooked_quests = hook_gen.add_hooks_to_quests(all_quests_by_type)
    hooked_output_file = os.path.join(output_dir, "generated_quests_with_hooks.json")
    hooked_output_data = {
        "world_data_source": data_filename,
        "quests": hooked_quests
    }
    with open(hooked_output_file, 'w', encoding='utf-8') as f:
        json.dump(hooked_output_data, f, indent=2, ensure_ascii=False)
    print(f"Quests with hooks saved to {hooked_output_file}")

if __name__ == "__main__":
    main()