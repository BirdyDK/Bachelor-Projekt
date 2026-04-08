import random

def get_new_id(world, prefix):
    world.next_id += 1
    return f"{prefix}_{world.next_id}"

def random_choice_weighted(choices_with_weights):
    if not choices_with_weights:
        return None
    total = sum(w for _, w in choices_with_weights)
    r = random.uniform(0, total)
    upto = 0
    for item, weight in choices_with_weights:
        upto += weight
        if upto >= r:
            return item
    return choices_with_weights[-1][0]