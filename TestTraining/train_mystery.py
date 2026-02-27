import torch
import os
from datasets import load_dataset
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

print(f"CUDA available: {torch.cuda.is_available()}")
print(f"Device count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"Current device: {torch.cuda.current_device()}")
    print(f"Device name: {torch.cuda.get_device_name(0)}")
else:
    print("No CUDA, this will take very long")

load_dotenv()

# 1. SETUP & DATA
MODEL_ID = "meta-llama/Llama-3.2-1B-Instruct" # You can change to Gemma-2b, SMOL, QWEN, or others
ACCESS_TOKEN = os.getenv("HF_TOKEN")
CSV_FILE = "TestTraining\\tranquilville_mysteries.csv"

# Login to HuggingFace with the token from .env
if ACCESS_TOKEN:
    login(token=ACCESS_TOKEN)
else:
    raise ValueError("HF_TOKEN not found in .env file. Please add your Hugging Face token.")

# Load dataset
dataset = load_dataset('csv', data_files=CSV_FILE, sep=';', quotechar='"', split='train')

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
    args=TrainingArguments(
        output_dir="./mystery_adapter",
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=3e-5,
        num_train_epochs=1,
        logging_steps=10,
        bf16=True, # Set to False if using CPU/older GPU
        save_strategy="epoch"
    ),
)

trainer.train()
model.save_pretrained("./TestTraining")
print("Training Complete! Adapter saved to ./TestTraining")
