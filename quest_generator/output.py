import csv
import json
from models import to_dict
from narrative import extract_atomic_actions

def write_example(writer, world, player, quest):
    """Write one example row to CSV."""
    world_dict = to_dict(world)
    player_dict = to_dict(player)
    quest_dict = to_dict(quest)
    atomic_actions = extract_atomic_actions(quest.structure)
    # Remove duplicates? Keep order as they appear
    # atomic_actions is a list of class names
    writer.writerow([
        json.dumps(world_dict),
        json.dumps(player_dict),
        json.dumps(atomic_actions),
        json.dumps(quest_dict),
        ""  # narrative placeholder; we'll generate separately
    ])