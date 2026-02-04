import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    BitsAndBytesConfig, 
    TrainingArguments
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

# 1. SETUP & DATA
MODEL_ID = "meta-llama/Llama-3.2-1B-Instruct" # You can change to Gemma-2b or others
CSV_FILE = "tranquilville_mysteries.csv"

dataset = load_dataset('csv', data_files=CSV_FILE, split='train')

def format_mystery(example):
    # We use the 'input_names_only' as the prompt and 'output' as the target
    text = f"### Instruction: Create a mystery story from these details:\n{example['input_names_only']}\n\n### Response: {example['output']}"
    return {"text": text}

dataset = dataset.map(format_mystery)

# 2. LOAD MODEL IN 4-BIT (Memory Efficient)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID, 
    quantization_config=bnb_config, 
    device_map="auto",
    trust_remote_code=True
)
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
tokenizer.pad_token = tokenizer.eos_token

# 3. CONFIGURE LoRA (The PEFT part)
model = prepare_model_for_kbit_training(model)
peft_config = LoraConfig(
    r=32, 
    lora_alpha=64,
    target_modules="all-linear", # Targets all important layers for better creativity
    lora_dropout=0.1,
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, peft_config)

# 4. TRAIN
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    args=TrainingArguments(
        output_dir="./mystery_adapter",
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        num_train_epochs=3,
        logging_steps=10,
        fp16=True, # Set to False if using CPU/older GPU
        save_strategy="epoch"
    ),
)

trainer.train()
model.save_pretrained("./final_mystery_adapter")
print("Training Complete! Adapter saved to ./final_mystery_adapter")
