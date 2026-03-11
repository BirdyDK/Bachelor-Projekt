import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import re

# Configuration
BASE_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
ADAPTER_PATH = "./TestTraining/Adapter"  # Path to your trained adapter
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def load_mystery_model(adapter_path=ADAPTER_PATH):
    """Load the base model and trained adapter"""
    print(f"Loading base model: {BASE_MODEL}")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    tokenizer.pad_token = tokenizer.eos_token
    
    # Load base model
    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # Load and merge adapter
    print(f"Loading adapter from: {adapter_path}")
    model = PeftModel.from_pretrained(model, adapter_path)
    model.eval()
    
    return model, tokenizer

def format_mystery_input(input_text, input_type="structured"):
    """
    Format the input to match training format.
    
    Args:
        input_text: The mystery details
        input_type: "structured" for full format, "simple" for simple format
    """
    if input_type == "simple":
        # Convert simple input to structured format
        # Example: "Who: Silas. Where: Forge. Victim: Mayor." 
        # -> full structured format
        
        # Extract parts using regex
        who_match = re.search(r"Who:\s*([^.]+)", input_text)
        where_match = re.search(r"Where:\s*([^.]+)", input_text)
        victim_match = re.search(r"Victim:\s*([^.]+)", input_text)
        method_match = re.search(r"Method:\s*([^.]+)", input_text)
        
        who = who_match.group(1).strip() if who_match else "Unknown"
        where = where_match.group(1).strip() if where_match else "Unknown"
        victim = victim_match.group(1).strip() if victim_match else "Unknown"
        method = method_match.group(1).strip() if method_match else "unknown method"
        
        # Build structured prompt matching training format
        structured_prompt = f"""MYSTERY SETUP:

OPENING SCENE SETTING:
Who: {who}
Where: {where}
When: unknown
What: unknown

MURDER DETAILS:
Victim: {victim}
Method: {method}
Location: {where}

RED HERRING:
Character: Unknown
Action: unknown

MURDERER:
Unknown"""
        return structured_prompt
    else:
        # Assume input is already in structured format
        return input_text

def solve_mystery(model, tokenizer, input_text, input_type="structured", max_length=1500):
    """
    Generate a mystery story from input details.
    """
    # Format the input
    formatted_input = format_mystery_input(input_text, input_type)
    
    # Create messages with system prompt (same as training)
    messages = [
        {
            "role": "system", 
            "content": "You are a mystery writer. Always respond with a story containing these exact sections: OPENING SCENE:, PLOT SUMMARY:, INVESTIGATION CLUES:, and RED HERRING EXPLANATION:. Each section must start with the heading on its own line."
        },
        {
            "role": "user", 
            "content": f"Create a mystery story from these details:\n{formatted_input}"
        }
    ]
    
    # Apply chat template
    prompt = tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=True
    )
    
    # Tokenize
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    # Generate with improved parameters to prevent repetition
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_length,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            top_k=50,
            repetition_penalty=1.1,  # Prevents repetition
            no_repeat_ngram_size=3,   # Prevents repeating phrases
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )
    
    # Decode and clean up
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract only the assistant's response (remove the prompt)
    response = generated_text.split("assistant\n")[-1].strip()
    
    return response

def extract_sections(story):
    """Helper function to extract specific sections from the story"""
    sections = {
        "opening_scene": "",
        "plot_summary": "",
        "investigation_clues": "",
        "red_herring": ""
    }
    
    # Define section patterns
    patterns = {
        "opening_scene": r"OPENING SCENE:(.*?)(?=PLOT SUMMARY:|$)",
        "plot_summary": r"PLOT SUMMARY:(.*?)(?=INVESTIGATION CLUES:|$)",
        "investigation_clues": r"INVESTIGATION CLUES:(.*?)(?=RED HERRING EXPLANATION:|$)",
        "red_herring": r"RED HERRING EXPLANATION:(.*?)(?=$)"
    }
    
    for section, pattern in patterns.items():
        match = re.search(pattern, story, re.DOTALL | re.IGNORECASE)
        if match:
            sections[section] = match.group(1).strip()
    
    return sections

# Main execution
if __name__ == "__main__":
    # Load the model
    print("Loading mystery model...")
    model, tokenizer = load_mystery_model()
    
    # Test cases
    test_cases = [
        {
            "name": "Test 1 - Structured Input",
            "input": """MYSTERY SETUP:

OPENING SCENE SETTING:
Who: Silas the Blacksmith, Margaret the Baker
Where: The Village Forge
When: midnight
What: heated argument

MURDER DETAILS:
Victim: Mayor Higgins
Method: poisoned
Location: The Forge

RED HERRING:
Character: Margaret the Baker
Action: was seen fleeing with a vial

MURDERER:
Silas the Blacksmith""",
            "type": "structured"
        },
        {
            "name": "Test 2 - Simple Input",
            "input": "Who: Eleanor the Librarian. Where: The Library. Victim: Professor Aldridge. Method: stabbing.",
            "type": "simple"
        },
        {
            "name": "Test 3 - Minimal Input",
            "input": "Who: Thomas the Gardener. Victim: Lady Winchester.",
            "type": "simple"
        }
    ]
    
    # Run tests
    for test in test_cases:
        print("\n" + "="*80)
        print(f"📝 {test['name']}")
        print("="*80)
        print(f"Input: {test['input']}")
        print("-"*80)
        
        try:
            story = solve_mystery(
                model, 
                tokenizer, 
                test['input'], 
                input_type=test['type'],
                max_length=1200
            )
            
            print("\n📖 Generated Mystery:")
            print(story)
            
            # Optional: Extract and display sections
            sections = extract_sections(story)
            if any(sections.values()):
                print("\n📋 Extracted Sections:")
                for section_name, content in sections.items():
                    if content:
                        print(f"\n{section_name.upper()}:")
                        print(content[:200] + "..." if len(content) > 200 else content)
                        
        except Exception as e:
            print(f"❌ Error generating story: {e}")
    
    print("\n✅ Testing complete!")