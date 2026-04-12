import torch
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from typing import Dict, Any, Optional

# Configuration – adjust these paths as needed
BASE_MODEL = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
ADAPTER_PATH = "./TestTraining/Results/SmolLM2-1.7B-Instruct_ebs8_lr5e-05_r32_epochs3"

class SLMQuestGenerator:
    _instance = None
    _model = None
    _tokenizer = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _load_model(self):
        if self._model is None:
            print("Loading SLM model (this may take a moment)...")
            self._model = AutoModelForCausalLM.from_pretrained(
                BASE_MODEL,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            self._tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
            self._model = PeftModel.from_pretrained(self._model, ADAPTER_PATH)
            self._model.eval()
            print("Model loaded.")

    def generate_quest(self, world_state: Dict[str, Any]) -> Optional[str]:
        """Generate a quest using the SLM based on the given world state."""
        self._load_model()

        # Convert world state to a compact JSON string (only include relevant sections)
        # We'll extract NPCs, Factions, Locations, Enemies, Items, and Player
        state_subset = {
            "NPCs": world_state.get("npcs", {}),
            "Factions": world_state.get("factions", {}),
            "Locations": world_state.get("locations", {}),
            "Enemies": world_state.get("enemies", {}),
            "Items": world_state.get("items", {}),
            "Player": world_state.get("player", {})
        }
        input_json = json.dumps(state_subset, separators=(',', ':'), ensure_ascii=False)

        # Build prompt exactly as in use_mystery.py (system + user)
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
                '{"Quest": {"Name": "The Cave Menace", "Giver": "Brom", "Actions": ["goto Dark Cave", "kill Goblin", "goto Keep", "report Brom"]}}\n\n'
                "Brom is tired of the goblins in the Dark Cave. Go kill their leader and report back."
            )
        }
        user_message = {
            "role": "user",
            "content": f"Game state:\n{input_json}"
        }
        messages = [system_message, user_message]
        prompt = self._tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

        inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)
        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=1000,
                temperature=0.7,
                do_sample=True
            )
        full_output = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
        # The output contains the prompt + generated text. Extract only the assistant's part.
        # Since we used chat template, the generated part starts after the assistant turn.
        # A simple approach: take everything after the last occurrence of "assistant".
        # But we can also just return the whole thing and let the user see it.
        return full_output