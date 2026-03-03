import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL = "meta-llama/Llama-3.2-1B-Instruct"
ADAPTER_PATH = "./../mystery_adapter"

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
    prompt = f"### Instruction: Create a mystery story from these details:\n{input_text}\n\n### Response:"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    outputs = model.generate(
        **inputs, 
        max_new_tokens=1000, 
        temperature=0.7, 
        do_sample=True
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Test it with a new prompt
test_input = "Who: Silas the Blacksmith. Where: The Forge. Victim: Mayor Higgins."
print(solve_mystery(test_input))
