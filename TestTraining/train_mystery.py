import torch
import os
import pandas as pd
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    BitsAndBytesConfig, 
    TrainingArguments
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
from huggingface_hub import login
from dotenv import load_dotenv
import gc

print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Device name: {torch.cuda.get_device_name(0)}")
    print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
else:
    print("No CUDA, this will take very long")

load_dotenv()

# 1. SETUP & DATA
MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"  # Using instruct version
CSV_FILE = "TestTraining/tranquilville_mysteries.csv"
OUTPUT_DIR = "./TestTraining/Adapter"

# Clear GPU cache
torch.cuda.empty_cache()
gc.collect()

# 2. LOAD TOKENIZER FIRST
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"  # Important for causal LM

# 3. LOAD AND FORMAT DATASET
def load_and_format_dataset(csv_path):
    """Load CSV and format with system prompt and consistent structure"""
    df = pd.read_csv(csv_path, sep=';', quotechar='"')
    
    def format_with_system_prompt(row):
        # System message to enforce output structure
        system_message = {
            "role": "system", 
            "content": "You are a mystery writer. Always respond with a story containing these exact sections: OPENING SCENE:, PLOT SUMMARY:, INVESTIGATION CLUES:, and RED HERRING EXPLANATION:. Each section must start with the heading on its own line."
        }
        
        # User message with the structured input
        user_message = {
            "role": "user", 
            "content": f"Create a mystery story from these details:\n{row['input_names_only']}"
        }
        
        # Assistant message with the full output
        assistant_message = {
            "role": "assistant", 
            "content": row['output']
        }
        
        # Apply chat template
        messages = [system_message, user_message, assistant_message]
        text = tokenizer.apply_chat_template(messages, tokenize=False)
        return {"text": text}
    
    # Create dataset and apply formatting
    dataset = Dataset.from_pandas(df)
    dataset = dataset.map(format_with_system_prompt)
    dataset = dataset.shuffle(seed=42)
    
    # Split into train/validation
    split_dataset = dataset.train_test_split(test_size=0.1, seed=42)
    return split_dataset["train"], split_dataset["test"]

print("Loading and formatting dataset...")
train_dataset, eval_dataset = load_and_format_dataset(CSV_FILE)
print(f"Train samples: {len(train_dataset)}, Eval samples: {len(eval_dataset)}")

# 4. LOAD MODEL WITH 4-BIT QUANTIZATION
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID, 
    quantization_config=bnb_config, 
    device_map="auto",
    trust_remote_code=True,
)

# 5. CONFIGURE LORA (Optimized for 0.5B model)
model = prepare_model_for_kbit_training(model)

# Enable gradient checkpointing to save memory
model.gradient_checkpointing_enable()

peft_config = LoraConfig(
    r=16,  # Reduced from 32 for better generalization with smaller model
    lora_alpha=32,  # Adjusted proportionally
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],  # Specific modules instead of "all-linear"
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, peft_config)
model.print_trainable_parameters()  # Shows % of trainable parameters

# 6. TRAINING ARGUMENTS
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    num_train_epochs=2, 
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,  # Slightly higher for LoRA
    weight_decay=0.01,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
    logging_steps=10,
    eval_strategy="steps",
    eval_steps=100,
    save_strategy="steps",
    save_steps=100,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    bf16=True,
    gradient_checkpointing=True,
    optim="paged_adamw_8bit",
    max_grad_norm=0.3,
    remove_unused_columns=False,
)

# 7. TRAINER
trainer = SFTTrainer(
    model=model,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    args=training_args,
)

# 8. TRAIN AND SAVE
print("Starting training...")
trainer.train()

# Save the final model
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print(f"Training Complete! Model saved to {OUTPUT_DIR}")

# Optional: Merge and save full model (if you want a standalone model)
# from peft import PeftModel
# merged_model = model.merge_and_unload()
# merged_model.save_pretrained(f"{OUTPUT_DIR}_merged")