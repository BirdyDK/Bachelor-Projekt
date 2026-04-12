from typing import Union, TYPE_CHECKING, List, Any, Dict
import random
import json

if TYPE_CHECKING:
    pass

# Atomic Action Classes
class Terminal: pass
class Damage: pass
class Defend: pass
class Explore: pass
class Gather: pass
class Give: pass
class Goto: pass
class Kill: pass
class Read: pass
class Report: pass
class Stealth: pass
class Take: pass

# Forward declarations for recursive types
rule_goto = Union['goto_terminal', 'goto_explore', 'goto_learn']
rule_learn = Union['learn_terminal', 'learn_read']
rule_get = Union['get_terminal', 'get_steal', 'get_gather']
rule_steal = Union['steal_stealth', 'steal_kill']
rule_kill = Union['kill_kill']

# Rule Classes
class goto_terminal:
    terminal: Terminal

class goto_explore:
    explore: Explore

class goto_learn:
    learn: rule_learn
    goto: Goto

class learn_terminal:
    terminal: Terminal

class learn_read:
    goto: rule_goto
    get: rule_get
    read: Read

class get_terminal:
    terminal: Terminal

class get_steal:
    steal: rule_steal

class get_gather:
    goto: rule_goto
    gather: Gather

class steal_stealth:
    goto: rule_goto
    stealth: Stealth
    take: Take

class steal_kill:
    goto: rule_goto
    kill: rule_kill
    take: Take

class kill_kill:
    goto: rule_goto
    kill: Kill

# Quest Structure Classes
class AttackThreateningEntities:
    """
    <goto> damage <goto> report
    Go somewhere, damage something, go somewhere else, report
    """
    first_goto: rule_goto
    damage: Damage
    second_goto: rule_goto
    report: Report

class RecoverStolenItem:
    """
    <get> <goto> give
    Get something, go somewhere, give it
    """
    get: rule_get
    goto: rule_goto
    give: Give

class GuardEntity:
    """
    <goto> defend
    Go somewhere and defend
    """
    goto: rule_goto
    defend: Defend

class AttackEnemy:
    """
    <goto> damage
    Go somewhere and damage
    """
    goto: rule_goto
    damage: Damage

class StealStuff:
    """
    <goto> <steal> <goto> give
    Go somewhere, steal something, go somewhere else, give it
    """
    first_goto: rule_goto
    steal: rule_steal
    second_goto: rule_goto
    give: Give

class KillEnemies:
    """
    <goto> <kill> <goto> report
    Go somewhere, kill someone, go somewhere else, report
    """
    first_goto: rule_goto
    kill: rule_kill
    second_goto: rule_goto
    report: Report

# Quest wrapper class
class Quest:
    """Wrapper class that can hold any quest structure"""
    quest: Union[
        AttackThreateningEntities,
        RecoverStolenItem,
        GuardEntity,
        AttackEnemy,
        StealStuff,
        KillEnemies
    ]

# Random Quest Generator
class RandomQuestGenerator:
    """Generates random quests following the grammar rules"""
    
    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth
        self.current_depth = 0
        
        # Available atomic actions for terminal cases
        self.atomic_actions = [
            Terminal, Damage, Defend, Explore, Gather, 
            Give, Goto, Kill, Read, Report, Stealth, Take
        ]
    
    def reset_depth(self):
        """Reset the depth counter for a new generation"""
        self.current_depth = 0
    
    def increment_depth(self) -> bool:
        """Increment depth and check if max depth reached"""
        self.current_depth += 1
        return self.current_depth >= self.max_depth
    
    def random_atomic(self, action_class):
        """Create a random atomic action instance"""
        return action_class()
    
    def random_terminal(self):
        """Create a random terminal action (for base cases)"""
        action_class = random.choice(self.atomic_actions)
        return action_class()
    
    def generate_goto(self) -> rule_goto:
        """Randomly generate a goto rule"""
        if self.increment_depth():
            # Base case: terminal or explore
            if random.random() < 0.5:
                goto = goto_terminal()
                goto.terminal = self.random_atomic(Terminal)
                return goto
            else:
                goto = goto_explore()
                goto.explore = self.random_atomic(Explore)
                return goto
        
        # Recursive case: choose randomly
        choice = random.random()
        
        if choice < 0.33:  # terminal
            goto = goto_terminal()
            goto.terminal = self.random_atomic(Terminal)
            return goto
        elif choice < 0.66:  # explore
            goto = goto_explore()
            goto.explore = self.random_atomic(Explore)
            return goto
        else:  # learn
            goto = goto_learn()
            goto.learn = self.generate_learn()
            goto.goto = self.random_atomic(Goto)
            return goto
    
    def generate_learn(self) -> rule_learn:
        """Randomly generate a learn rule"""
        if self.increment_depth():
            # Base case: terminal
            learn = learn_terminal()
            learn.terminal = self.random_atomic(Terminal)
            return learn
        
        # Choose between terminal and read
        if random.random() < 0.3:  # terminal
            learn = learn_terminal()
            learn.terminal = self.random_atomic(Terminal)
            return learn
        else:  # read
            learn = learn_read()
            learn.goto = self.generate_goto()
            learn.get = self.generate_get()
            learn.read = self.random_atomic(Read)
            return learn
    
    def generate_get(self) -> rule_get:
        """Randomly generate a get rule"""
        if self.increment_depth():
            # Base case: terminal
            get = get_terminal()
            get.terminal = self.random_atomic(Terminal)
            return get
        
        # Choose between terminal, steal, and gather
        choice = random.random()
        
        if choice < 0.2:  # terminal
            get = get_terminal()
            get.terminal = self.random_atomic(Terminal)
            return get
        elif choice < 0.6:  # steal
            get = get_steal()
            get.steal = self.generate_steal()
            return get
        else:  # gather
            get = get_gather()
            get.goto = self.generate_goto()
            get.gather = self.random_atomic(Gather)
            return get
    
    def generate_steal(self) -> rule_steal:
        """Randomly generate a steal rule"""
        if self.increment_depth():
            # Default to stealth if max depth
            steal = steal_stealth()
            steal.goto = self.generate_goto()
            steal.stealth = self.random_atomic(Stealth)
            steal.take = self.random_atomic(Take)
            return steal
        
        # Choose between stealth and kill
        if random.random() < 0.5:  # stealth
            steal = steal_stealth()
            steal.goto = self.generate_goto()
            steal.stealth = self.random_atomic(Stealth)
            steal.take = self.random_atomic(Take)
            return steal
        else:  # kill
            steal = steal_kill()
            steal.goto = self.generate_goto()
            steal.kill = self.generate_kill()
            steal.take = self.random_atomic(Take)
            return steal
    
    def generate_kill(self) -> rule_kill:
        """Randomly generate a kill rule"""
        if self.increment_depth():
            # Base case: simple kill
            kill = kill_kill()
            kill.goto = self.generate_goto()
            kill.kill = self.random_atomic(Kill)
            return kill
        
        # Always use kill_kill (only one option)
        kill = kill_kill()
        kill.goto = self.generate_goto()
        kill.kill = self.random_atomic(Kill)
        return kill
    
    def generate_quest(self) -> Quest:
        """Randomly generate a complete quest"""
        self.reset_depth()
        
        # Choose a random quest type
        quest_types = [
            self.generate_attack_threatening,
            self.generate_recover_stolen,
            self.generate_guard_entity,
            self.generate_attack_enemy,
            self.generate_steal_stuff,
            self.generate_kill_enemies
        ]
        
        quest_instance = random.choice(quest_types)()
        
        # Wrap in Quest class
        quest = Quest()
        quest.quest = quest_instance
        return quest
    
    def generate_attack_threatening(self) -> AttackThreateningEntities:
        """Generate an Attack Threatening Entities quest"""
        quest = AttackThreateningEntities()
        quest.first_goto = self.generate_goto()
        quest.damage = self.random_atomic(Damage)
        quest.second_goto = self.generate_goto()
        quest.report = self.random_atomic(Report)
        return quest
    
    def generate_recover_stolen(self) -> RecoverStolenItem:
        """Generate a Recover Stolen Item quest"""
        quest = RecoverStolenItem()
        quest.get = self.generate_get()
        quest.goto = self.generate_goto()
        quest.give = self.random_atomic(Give)
        return quest
    
    def generate_guard_entity(self) -> GuardEntity:
        """Generate a Guard Entity quest"""
        quest = GuardEntity()
        quest.goto = self.generate_goto()
        quest.defend = self.random_atomic(Defend)
        return quest
    
    def generate_attack_enemy(self) -> AttackEnemy:
        """Generate an Attack Enemy quest"""
        quest = AttackEnemy()
        quest.goto = self.generate_goto()
        quest.damage = self.random_atomic(Damage)
        return quest
    
    def generate_steal_stuff(self) -> StealStuff:
        """Generate a Steal Stuff quest"""
        quest = StealStuff()
        quest.first_goto = self.generate_goto()
        quest.steal = self.generate_steal()
        quest.second_goto = self.generate_goto()
        quest.give = self.random_atomic(Give)
        return quest
    
    def generate_kill_enemies(self) -> KillEnemies:
        """Generate a Kill Enemies quest"""
        quest = KillEnemies()
        quest.first_goto = self.generate_goto()
        quest.kill = self.generate_kill()
        quest.second_goto = self.generate_goto()
        quest.report = self.random_atomic(Report)
        return quest

# JSON Converter
class QuestToJSON:
    """Converts quest structures to JSON-compatible dictionaries"""
    
    @staticmethod
    def convert(obj: Any) -> Dict:
        """
        Recursively converts any quest structure to a JSON-serializable dictionary
        """
        if obj is None:
            return None
        
        match obj:
            # Atomic Actions
            case Terminal():
                return {"type": "Terminal"}
            case Damage():
                return {"type": "Damage"}
            case Defend():
                return {"type": "Defend"}
            case Explore():
                return {"type": "Explore"}
            case Gather():
                return {"type": "Gather"}
            case Give():
                return {"type": "Give"}
            case Goto():
                return {"type": "Goto"}
            case Kill():
                return {"type": "Kill"}
            case Read():
                return {"type": "Read"}
            case Report():
                return {"type": "Report"}
            case Stealth():
                return {"type": "Stealth"}
            case Take():
                return {"type": "Take"}
            
            # Rule Classes
            case goto_terminal():
                return {
                    "rule": "goto_terminal",
                    "terminal": QuestToJSON.convert(obj.terminal)
                }
            
            case goto_explore():
                return {
                    "rule": "goto_explore",
                    "explore": QuestToJSON.convert(obj.explore)
                }
            
            case goto_learn():
                return {
                    "rule": "goto_learn",
                    "learn": QuestToJSON.convert(obj.learn),
                    "goto": QuestToJSON.convert(obj.goto)
                }
            
            case learn_terminal():
                return {
                    "rule": "learn_terminal",
                    "terminal": QuestToJSON.convert(obj.terminal)
                }
            
            case learn_read():
                return {
                    "rule": "learn_read",
                    "goto": QuestToJSON.convert(obj.goto),
                    "get": QuestToJSON.convert(obj.get),
                    "read": QuestToJSON.convert(obj.read)
                }
            
            case get_terminal():
                return {
                    "rule": "get_terminal",
                    "terminal": QuestToJSON.convert(obj.terminal)
                }
            
            case get_steal():
                return {
                    "rule": "get_steal",
                    "steal": QuestToJSON.convert(obj.steal)
                }
            
            case get_gather():
                return {
                    "rule": "get_gather",
                    "goto": QuestToJSON.convert(obj.goto),
                    "gather": QuestToJSON.convert(obj.gather)
                }
            
            case steal_stealth():
                return {
                    "rule": "steal_stealth",
                    "goto": QuestToJSON.convert(obj.goto),
                    "stealth": QuestToJSON.convert(obj.stealth),
                    "take": QuestToJSON.convert(obj.take)
                }
            
            case steal_kill():
                return {
                    "rule": "steal_kill",
                    "goto": QuestToJSON.convert(obj.goto),
                    "kill": QuestToJSON.convert(obj.kill),
                    "take": QuestToJSON.convert(obj.take)
                }
            
            case kill_kill():
                return {
                    "rule": "kill_kill",
                    "goto": QuestToJSON.convert(obj.goto),
                    "kill": QuestToJSON.convert(obj.kill)
                }
            
            # Quest Structures
            case AttackThreateningEntities():
                return {
                    "quest": "AttackThreateningEntities",
                    "first_goto": QuestToJSON.convert(obj.first_goto),
                    "damage": QuestToJSON.convert(obj.damage),
                    "second_goto": QuestToJSON.convert(obj.second_goto),
                    "report": QuestToJSON.convert(obj.report)
                }
            
            case RecoverStolenItem():
                return {
                    "quest": "RecoverStolenItem",
                    "get": QuestToJSON.convert(obj.get),
                    "goto": QuestToJSON.convert(obj.goto),
                    "give": QuestToJSON.convert(obj.give)
                }
            
            case GuardEntity():
                return {
                    "quest": "GuardEntity",
                    "goto": QuestToJSON.convert(obj.goto),
                    "defend": QuestToJSON.convert(obj.defend)
                }
            
            case AttackEnemy():
                return {
                    "quest": "AttackEnemy",
                    "goto": QuestToJSON.convert(obj.goto),
                    "damage": QuestToJSON.convert(obj.damage)
                }
            
            case StealStuff():
                return {
                    "quest": "StealStuff",
                    "first_goto": QuestToJSON.convert(obj.first_goto),
                    "steal": QuestToJSON.convert(obj.steal),
                    "second_goto": QuestToJSON.convert(obj.second_goto),
                    "give": QuestToJSON.convert(obj.give)
                }
            
            case KillEnemies():
                return {
                    "quest": "KillEnemies",
                    "first_goto": QuestToJSON.convert(obj.first_goto),
                    "kill": QuestToJSON.convert(obj.kill),
                    "second_goto": QuestToJSON.convert(obj.second_goto),
                    "report": QuestToJSON.convert(obj.report)
                }
            
            case Quest():
                return {
                    "wrapper": "Quest",
                    "quest": QuestToJSON.convert(obj.quest)
                }
            
            case _:
                return {"unknown_type": str(type(obj))}

    @staticmethod
    def to_json(obj: Any, indent: int = 2) -> str:
        """
        Convert a quest structure to a formatted JSON string
        """
        return json.dumps(QuestToJSON.convert(obj), indent=indent)

# Quest Structure Handler with match statements
class QuestStructurePrinter:
    """Recursively traverses and prints quest structures using match"""
    
    def __init__(self, indent_size: int = 2):
        self.indent_size = indent_size
        self.indent_level = 0
    
    def indent(self) -> str:
        """Returns the current indentation string"""
        return " " * (self.indent_level * self.indent_size)
    
    def print_with_indent(self, text: str):
        """Prints text with current indentation"""
        print(f"{self.indent()}{text}")
    
    def print_atomic_action(self, obj: Any, action_name: str):
        """Prints an atomic action"""
        self.print_with_indent(f"⚡ {action_name}")
    
    def traverse(self, obj: Any, context: str = ""):
        """
        Recursively traverses any quest structure and prints its components
        using Python's match statement
        """
        if obj is None:
            return
        
        match obj:
            # Atomic Actions
            case Terminal():
                self.print_atomic_action(obj, "TERMINAL")
            case Damage():
                self.print_atomic_action(obj, "DAMAGE")
            case Defend():
                self.print_atomic_action(obj, "DEFEND")
            case Explore():
                self.print_atomic_action(obj, "EXPLORE")
            case Gather():
                self.print_atomic_action(obj, "GATHER")
            case Give():
                self.print_atomic_action(obj, "GIVE")
            case Goto():
                self.print_atomic_action(obj, "GOTO")
            case Kill():
                self.print_atomic_action(obj, "KILL")
            case Read():
                self.print_atomic_action(obj, "READ")
            case Report():
                self.print_atomic_action(obj, "REPORT")
            case Stealth():
                self.print_atomic_action(obj, "STEALTH")
            case Take():
                self.print_atomic_action(obj, "TAKE")
            
            # Rule Classes
            case goto_terminal():
                self.print_with_indent(f"📋 goto_terminal:")
                self.indent_level += 1
                self.traverse(obj.terminal)
                self.indent_level -= 1
            
            case goto_explore():
                self.print_with_indent(f"📋 goto_explore:")
                self.indent_level += 1
                self.traverse(obj.explore)
                self.indent_level -= 1
            
            case goto_learn():
                self.print_with_indent(f"📋 goto_learn:")
                self.indent_level += 1
                self.traverse(obj.learn)
                self.traverse(obj.goto)
                self.indent_level -= 1
            
            case learn_terminal():
                self.print_with_indent(f"📋 learn_terminal:")
                self.indent_level += 1
                self.traverse(obj.terminal)
                self.indent_level -= 1
            
            case learn_read():
                self.print_with_indent(f"📋 learn_read:")
                self.indent_level += 1
                self.traverse(obj.goto)
                self.traverse(obj.get)
                self.traverse(obj.read)
                self.indent_level -= 1
            
            case get_terminal():
                self.print_with_indent(f"📋 get_terminal:")
                self.indent_level += 1
                self.traverse(obj.terminal)
                self.indent_level -= 1
            
            case get_steal():
                self.print_with_indent(f"📋 get_steal:")
                self.indent_level += 1
                self.traverse(obj.steal)
                self.indent_level -= 1
            
            case get_gather():
                self.print_with_indent(f"📋 get_gather:")
                self.indent_level += 1
                self.traverse(obj.goto)
                self.traverse(obj.gather)
                self.indent_level -= 1
            
            case steal_stealth():
                self.print_with_indent(f"📋 steal_stealth:")
                self.indent_level += 1
                self.traverse(obj.goto)
                self.traverse(obj.stealth)
                self.traverse(obj.take)
                self.indent_level -= 1
            
            case steal_kill():
                self.print_with_indent(f"📋 steal_kill:")
                self.indent_level += 1
                self.traverse(obj.goto)
                self.traverse(obj.kill)
                self.traverse(obj.take)
                self.indent_level -= 1
            
            case kill_kill():
                self.print_with_indent(f"📋 kill_kill:")
                self.indent_level += 1
                self.traverse(obj.goto)
                self.traverse(obj.kill)
                self.indent_level -= 1
            
            # Quest Structures
            case AttackThreateningEntities():
                self.print_with_indent(f"🎯 QUEST: Attack Threatening Entities")
                self.indent_level += 1
                self.traverse(obj.first_goto)
                self.traverse(obj.damage)
                self.traverse(obj.second_goto)
                self.traverse(obj.report)
                self.indent_level -= 1
            
            case RecoverStolenItem():
                self.print_with_indent(f"🎯 QUEST: Recover Stolen Item")
                self.indent_level += 1
                self.traverse(obj.get)
                self.traverse(obj.goto)
                self.traverse(obj.give)
                self.indent_level -= 1
            
            case GuardEntity():
                self.print_with_indent(f"🎯 QUEST: Guard Entity")
                self.indent_level += 1
                self.traverse(obj.goto)
                self.traverse(obj.defend)
                self.indent_level -= 1
            
            case AttackEnemy():
                self.print_with_indent(f"🎯 QUEST: Attack Enemy")
                self.indent_level += 1
                self.traverse(obj.goto)
                self.traverse(obj.damage)
                self.indent_level -= 1
            
            case StealStuff():
                self.print_with_indent(f"🎯 QUEST: Steal Stuff")
                self.indent_level += 1
                self.traverse(obj.first_goto)
                self.traverse(obj.steal)
                self.traverse(obj.second_goto)
                self.traverse(obj.give)
                self.indent_level -= 1
            
            case KillEnemies():
                self.print_with_indent(f"🎯 QUEST: Kill Enemies")
                self.indent_level += 1
                self.traverse(obj.first_goto)
                self.traverse(obj.kill)
                self.traverse(obj.second_goto)
                self.traverse(obj.report)
                self.indent_level -= 1
            
            case Quest():
                self.print_with_indent(f"📦 Quest Wrapper:")
                self.indent_level += 1
                self.traverse(obj.quest)
                self.indent_level -= 1
            
            case _:
                self.print_with_indent(f"❓ Unknown type: {type(obj).__name__}")

# Example usage
if __name__ == "__main__":
    # Create the printer
    printer = QuestStructurePrinter(indent_size=2)
    
    # Create JSON converter
    json_converter = QuestToJSON()
    
    # Create random quest generator
    generator = RandomQuestGenerator(max_depth=4)
    
    # Generate and print 3 random quests in both formats
    for i in range(3):
        print(f"\n{'='*50}")
        print(f"RANDOM QUEST {i+1}")
        print(f"{'='*50}")
        
        # Generate random quest
        random_quest = generator.generate_quest()
        
        # Print as tree structure
        print("\n📊 TREE STRUCTURE:")
        printer.traverse(random_quest)
        
        # Print as JSON
        print("\n📋 JSON FORMAT:")
        print(json_converter.to_json(random_quest, indent=2))
        
        print()