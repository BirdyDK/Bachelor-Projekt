import csv
import json
import enum
import os
from world_gen import generate_world
from player_gen import generate_player
from quest_gen import generate_quest
from narrative import generate_narrative, extract_atomic_actions

def main(num_examples=100):
    os.makedirs("quest_generator", exist_ok=True)
    output_path = os.path.join("quest_generator", "quest_data.csv")

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(['world_state', 'player_state', 'atomic_actions', 'quest_json', 'narrative'])

        for i in range(num_examples):
            world = generate_world()
            world, player = generate_player(world)
            quest = generate_quest(world, player)
            narrative = generate_narrative(quest, world, player)

            def serialize(obj):
                if hasattr(obj, '__dict__'):
                    return obj.__dict__
                if isinstance(obj, enum.Enum):
                    return obj.value
                return str(obj)

            world_json = json.dumps(world, default=serialize, indent=2)
            player_json = json.dumps(player, default=serialize, indent=2)
            atomic_json = json.dumps(extract_atomic_actions(quest.structure), indent=2)
            quest_json = json.dumps(quest, default=serialize, indent=2)

            writer.writerow([world_json, player_json, atomic_json, quest_json, narrative])

            if i % 10 == 0:
                print(f"Generated {i} examples")

    print(f"\nDone. Output written to {output_path}")

if __name__ == "__main__":
    main(100)