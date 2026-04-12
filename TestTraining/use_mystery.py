import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
ADAPTER_PATH = "./TestTraining/Results/SmolLM2-1.7B-Instruct_ebs8_lr5e-05_r32_epochs3"

# 1. Load Base Model
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL, 
    torch_dtype=torch.float16, 
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

# 2. Load the Adapter (The trained mystery "brain")
model = PeftModel.from_pretrained(model, ADAPTER_PATH)
model.eval()

# 3. Generate a Mystery
def solve_mystery(input_text):
    system_message = {
        "role": "system",
        "content": (
            "You are a quest generator for a fantasy RPG. Your output must strictly follow this two-part format:\n"
            "1. A JSON object: {\"Quest\": {\"Name\": \"...\", \"Giver\": \"...\", \"Actions\": [...]}}\n"
            "2. Two newlines, followed by a separate plain-text description.\n\n"
            "--- QUEST GENERATION LOGIC ---\n"
            "To generate 'Actions', start with a 'Quest Structure' and expand the <RULES> recursively until only Atomic Actions remain. "
            "Every final action must be a string in the format: 'action Target'.\n\n"
            "1. QUEST STRUCTURES (Initial Templates):\n"
            "- Attack threatening entities: <goto> damage <goto> report\n"
            "- Recover stolen item: <get> <goto> give\n"
            "- Guard entity: <goto> defend\n"
            "- Attack enemy: <goto> damage\n"
            "- Steal stuff: <goto> <steal> <goto> give\n"
            "- Kill enemies: <goto> <kill> <goto> report\n\n"
            "2. EXPANSION RULES (Replace <RULE> with one of its options):\n"
            "- <goto>  ::= terminal (already there) | explore | <learn> goto\n"
            "- <learn> ::= terminal (already known) | <goto> <get> read\n"
            "- <get>   ::= terminal (already have) | <steal> | <goto> gather\n"
            "- <steal> ::= <goto> stealth take | <goto> <kill> take\n"
            "- <kill>  ::= <goto> kill\n\n"
            "3. ATOMIC ACTIONS (Final Output Format):\n"
            "Each action must be paired with a target from the game state:\n"
            "- damage [Enemy], defend [NPC/Loc], explore [Loc], gather [Item], give [NPC], "
            "goto [Loc], kill [Enemy], read [Item], report [NPC], stealth [NPC], take [Item].\n\n"
            "--- EXAMPLE PROCESS ---\n"
            "Quest: Kill enemies\n"
            "Step 1 (Structure): <goto> <kill> <goto> report\n"
            "Step 2 (Expand <kill>): <goto> <goto> kill <goto> report\n"
            "Step 3 (Final Atomic): ['goto Shadowfen', 'goto Dark Cave', 'kill Goblin', 'goto Keep', 'report Brom']\n\n"
            "--- OUTPUT EXAMPLE ---\n"
            "{\"Quest\": {\"Name\": \"The Cave Menace\", \"Giver\": \"Brom\", \"Actions\": [\"goto Dark Cave\", \"kill Goblin\", \"goto Keep\", \"report Brom\"]}}\n\n"
            "Brom is tired of the goblins in the Dark Cave. Go kill their leader and report back."
        )
    }
    user_message = {
        "role": "user",
        "content": f"Game state:\n{input_text}"
    }
    messages = [system_message, user_message]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    # Tokenize and generate
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    outputs = model.generate(
        **inputs, 
        max_new_tokens=1000, 
        temperature=0.7, 
        do_sample=True
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Test it with a new prompt
test_input = """
    {""Factions"":{""Miners Guild"":{""Name"":""Miners Guild"",""Relations"":[{""Target"":""Wildborne Circle"",""Favorability"":""Ally""},{""Target"":""Iron Horde"",""Favorability"":""Enemy""},{""Target"":""Player"",""Favorability"":""Friendly""}],""Members"":[""Thalia Ironvein"",""Borak Ironhide""],""Treasury"":{""Gold"":500,""Iron Ore"":200},""FactionLog"":[]}},""NPCs"":{""Thalia Ironvein"":{""Name"":""Thalia Ironvein"",""Species"":""Dwarf"",""HomeLocation"":""Ironhold Keep"",""CurrentLocation"":""Ironhold Keep"",""Faction"":""Miners Guild"",""OwnedItems"":{""Iron Ore"":5,""Pickaxe"":1},""Role"":""Foreman"",""Relations"":[{""Target"":""Player"",""Favorability"":""Ally""}],""NPCLog"":[]}},""Locations"":{""Cinderfall Mine"":{""Name"":""Cinderfall Mine"",""Enemies"":[""Cave Troll"",""Cinder Elemental""],""Resources"":[""Iron Ore"",""Fire Crystal""]}},""Enemies"":{""Cave Troll"":{""Name"":""Cave Troll"",""Loot"":[""Troll Hide"",""Gold"",""Troll Bone""]}}}
"""
print(solve_mystery(test_input))
