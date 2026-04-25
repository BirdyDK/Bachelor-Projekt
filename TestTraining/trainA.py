import argparse
import time
from datetime import timedelta
import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

parser = argparse.ArgumentParser()
parser.add_argument("--model_id", type=str)
parser.add_argument("--batch_size", type=int)
parser.add_argument("--grad_accum", type=int, default=1)
parser.add_argument("--learning_rate", type=float)
parser.add_argument("--lora_r", type=int, default=16)
parser.add_argument("--lora_alpha", type=int, default=32)
parser.add_argument("--output_dir", type=str)
parser.add_argument("--epochs", type=int, default=1)
args = parser.parse_args()

CSV_FILE = "TestTraining/tranquilville_mysteries.csv"

dataset = load_dataset("csv", data_files=CSV_FILE, sep=";", quotechar='"', split="train")

def format_example(example):
    return {
        "text": (
            f"### Instruction:\n"
            f"Create a mystery story from these details:\n{example['input_names_only']}\n\n"
            f"### Response:\n{example['output']}"
        )
    }

dataset = dataset.map(format_example)

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

model = AutoModelForCausalLM.from_pretrained(
    args.model_id,
    quantization_config=bnb_config,
    device_map="auto"
)

tokenizer = AutoTokenizer.from_pretrained(args.model_id)
tokenizer.pad_token = tokenizer.eos_token

model = prepare_model_for_kbit_training(model)
peft_config = LoraConfig(
    r=args.lora_r,
    lora_alpha=args.lora_alpha,
    target_modules="all-linear",
    lora_dropout=0.1,
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, peft_config)

training_args = TrainingArguments(
    output_dir=args.output_dir,
    per_device_train_batch_size=args.batch_size,
    gradient_accumulation_steps=args.grad_accum,
    learning_rate=args.learning_rate,
    num_train_epochs=args.epochs,
    logging_steps=10,
    bf16=True,
    save_strategy="no",
    report_to="none"
)

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    args=training_args,
)

# Precise timing
start_time = time.perf_counter()
train_output = trainer.train()
end_time = time.perf_counter()

duration = end_time - start_time
duration_str = str(timedelta(seconds=int(duration)))

with open(f"{args.output_dir}/metrics.txt", "w") as f:
    f.write(f"experiment: {args.output_dir}\n")
    f.write(f"train_loss: {train_output.training_loss}\n")
    f.write(f"eval_loss: N/A\n")
    f.write(f"duration_seconds: {duration:.2f}\n")
    f.write(f"duration_hms: {duration_str}\n")

trainer.save_model(args.output_dir)
tokenizer.save_pretrained(args.output_dir)