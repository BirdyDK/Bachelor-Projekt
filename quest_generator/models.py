from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Union
import enum
import json

# -------------------- Enums --------------------
class Race(enum.Enum):
    HUMAN = "human"
    ELF = "elf"
    DWARF = "dwarf"
    ORC = "orc"
    HALFLING = "halfling"
    GNOME = "gnome"

class Profession(enum.Enum):
    ELDER = "elder"
    GUARD = "guard"
    SMITH = "smith"
    MERCHANT = "merchant"
    CIVILIAN = "civilian"
    DIPLOMAT = "diplomat"
    RANGER = "ranger"
    CHIEFTAIN = "chieftain"
    SHAMAN = "shaman"
    INVENTOR = "inventor"

class ItemType(enum.Enum):
    ARTIFACT = "artifact"
    TREASURE = "treasure"
    WEAPON = "weapon"
    DOCUMENT = "document"
    JEWELRY = "jewelry"
    POTION = "potion"
    TOOL = "tool"
    RELIGIOUS = "religious"
    CONTAINER = "container"
    HERB = "herb"
    CLOTHING = "clothing"
    BADGE = "badge"
    CRAFTED = "crafted"          # for player‑made items

class EventType(enum.Enum):
    KILL = "kill"
    STEAL = "steal"
    GIVE = "give"
    QUEST_GIVEN = "quest_given"
    QUEST_COMPLETED = "quest_completed"
    HELP = "help"
    GATHER = "gather"            # player gathers resource
    CRAFT = "craft"              # player crafts item
    FIGHT = "fight"              # NPCs fight each other
    ALLIANCE = "alliance"        # two factions become allied
    CONFLICT = "conflict"        # two factions become enemies
    TRADE = "trade"              # NPCs trade items

# -------------------- Factions --------------------
FACTIONS = [
    "The Crimson Hand",
    "The Silver Dawn",
    "The Emerald Circle",
    "The Iron Vanguard",
    "The Golden Lotus"
]

# -------------------- Entity Classes --------------------
@dataclass
class Item:
    id: str
    name: str
    type: ItemType
    description: str
    owner_id: Optional[str] = None          # NPC id, location id, or "player"
    location_id: Optional[str] = None       # if dropped

@dataclass
class Location:
    id: str
    name: str
    inhabitants: List[str] = field(default_factory=list)   # NPC ids
    items: List[str] = field(default_factory=list)         # item ids

@dataclass
class NPC:
    id: str
    name: str
    race: Race
    profession: Profession
    location_id: str
    faction: str                    # name of the faction
    allies: List[str] = field(default_factory=list)        # faction names this NPC personally considers allies
    enemies: List[str] = field(default_factory=list)       # faction names this NPC considers enemies
    inventory: List[str] = field(default_factory=list)      # item ids
    alive: bool = True

@dataclass
class Event:
    id: str
    timestamp: int
    type: EventType
    actor_id: Optional[str] = None   # NPC id, "player", or faction name
    target_id: Optional[str] = None
    item_id: Optional[str] = None
    description: str = ""

@dataclass
class WorldState:
    npcs: Dict[str, NPC]
    locations: Dict[str, Location]
    items: Dict[str, Item]
    events: List[Event] = field(default_factory=list)
    faction_relations: Dict[str, Dict[str, int]] = field(default_factory=dict)  # faction -> {other faction: relation score}
    next_id: int = 0

@dataclass
class PlayerState:
    inventory: List[str] = field(default_factory=list)      # item ids
    current_location_id: str = ""
    faction_reputation: Dict[str, int] = field(default_factory=dict) # faction name -> score
    action_log: List[Event] = field(default_factory=list)   # events where player is actor
    completed_quests: List[str] = field(default_factory=list)

# -------------------- Atomic Action Classes --------------------
class AtomicAction:
    pass

@dataclass
class Terminal(AtomicAction):
    pass

@dataclass
class Damage(AtomicAction):
    target_id: str

@dataclass
class Defend(AtomicAction):
    target_id: str
    location_id: str

@dataclass
class Explore(AtomicAction):
    location_id: str

@dataclass
class Gather(AtomicAction):
    item_id: str
    location_id: str

@dataclass
class Give(AtomicAction):
    item_id: str
    recipient_id: str

@dataclass
class Goto(AtomicAction):
    location_id: str

@dataclass
class Kill(AtomicAction):
    target_id: str

@dataclass
class Read(AtomicAction):
    information: str      # e.g., "the creature's weakness"
    location_id: str

@dataclass
class Report(AtomicAction):
    recipient_id: str
    information: str

@dataclass
class Stealth(AtomicAction):
    target_id: str
    location_id: str

@dataclass
class Take(AtomicAction):
    item_id: str
    owner_id: str

# -------------------- Grammar Rule Classes --------------------
@dataclass
class GotoTerminal:
    terminal: Terminal

@dataclass
class GotoExplore:
    explore: Explore

@dataclass
class GotoLearn:
    learn: 'LearnRule'
    goto: Goto

@dataclass
class LearnTerminal:
    terminal: Terminal

@dataclass
class LearnRead:
    goto: 'GotoRule'
    get: 'GetRule'
    read: Read

@dataclass
class GetTerminal:
    terminal: Terminal

@dataclass
class GetSteal:
    steal: 'StealRule'

@dataclass
class GetGather:
    goto: 'GotoRule'
    gather: Gather

@dataclass
class StealStealth:
    goto: 'GotoRule'
    stealth: Stealth
    take: Take

@dataclass
class StealKill:
    goto: 'GotoRule'
    kill: 'KillRule'
    take: Take

@dataclass
class KillKill:
    goto: 'GotoRule'
    kill: Kill

# Type aliases for recursive rules
GotoRule = Union[GotoTerminal, GotoExplore, GotoLearn]
LearnRule = Union[LearnTerminal, LearnRead]
GetRule = Union[GetTerminal, GetSteal, GetGather]
StealRule = Union[StealStealth, StealKill]
KillRule = KillKill

# -------------------- Quest Structure Classes --------------------
@dataclass
class AttackThreateningEntities:
    first_goto: GotoRule
    damage: Damage
    second_goto: GotoRule
    report: Report

@dataclass
class RecoverStolenItem:
    get: GetRule
    goto: GotoRule
    give: Give

@dataclass
class GuardEntity:
    goto: GotoRule
    defend: Defend

@dataclass
class AttackEnemy:
    goto: GotoRule
    damage: Damage

@dataclass
class StealStuff:
    first_goto: GotoRule
    steal: StealRule
    second_goto: GotoRule
    give: Give

@dataclass
class KillEnemies:
    first_goto: GotoRule
    kill: KillRule
    second_goto: GotoRule
    report: Report

# -------------------- Quest Wrapper --------------------
@dataclass
class Quest:
    giver_id: str                # NPC who gave the quest
    reason: str                  # e.g., "to save my village"
    structure: Union[AttackThreateningEntities, RecoverStolenItem, GuardEntity, AttackEnemy, StealStuff, KillEnemies]

# -------------------- Serialization Helpers --------------------
def to_dict(obj):
    """Convert dataclass to dict, handling Enums."""
    return asdict(obj, dict_factory=lambda x: {k: v.value if isinstance(v, enum.Enum) else v for k, v in x})

def to_json(obj):
    return json.dumps(to_dict(obj), indent=2)