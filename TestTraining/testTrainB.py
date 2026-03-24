import argparse
import time
from datetime import timedelta
import torch
import pandas as pd
from datasets import Dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
import gc

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

torch.cuda.empty_cache()
gc.collect()

tokenizer = AutoTokenizer.from_pretrained(args.model_id)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

def load_dataset_custom(csv_path):
    df = pd.read_csv(csv_path, sep=";", quotechar='"')

    def format_row(row):
        messages = [
            {"role": "system", "content": (
                "You are a mystery writer. Always respond with a story containing "
                "OPENING SCENE:, PLOT SUMMARY:, INVESTIGATION CLUES:, and RED HERRING EXPLANATION:."
            )},
            {"role": "user", "content": f"Create a mystery story from these details:\n{row['input_names_only']}"},
            {"role": "assistant", "content": row["output"]}
        ]
        return {"text": tokenizer.apply_chat_template(messages, tokenize=False)}

    dataset = Dataset.from_pandas(df)
    dataset = dataset.map(format_row)
    dataset = dataset.shuffle(seed=42)
    return dataset.train_test_split(test_size=0.1, seed=42)

train_dataset, eval_dataset = load_dataset_custom(CSV_FILE).values()

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True
)

model = AutoModelForCausalLM.from_pretrained(
    args.model_id,
    quantization_config=bnb_config,
    device_map="auto"
)

model = prepare_model_for_kbit_training(model)
model.gradient_checkpointing_enable()

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
    num_train_epochs=args.epochs,
    per_device_train_batch_size=args.batch_size,
    gradient_accumulation_steps=args.grad_accum,
    learning_rate=args.learning_rate,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
    logging_steps=10,
    eval_strategy="epoch",
    save_strategy="no",
    bf16=True,
    optim="paged_adamw_8bit",
    report_to="none"
)

trainer = SFTTrainer(
    model=model,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    args=training_args,
)

# Precise timing
start_time = time.perf_counter()
train_output = trainer.train()
eval_metrics = trainer.evaluate()
end_time = time.perf_counter()

duration = end_time - start_time
duration_str = str(timedelta(seconds=int(duration)))

with open(f"{args.output_dir}/metrics.txt", "w") as f:
    f.write(f"experiment: {args.output_dir}\n")
    f.write(f"train_loss: {train_output.training_loss}\n")
    f.write(f"eval_loss: {eval_metrics.get('eval_loss', 'N/A')}\n")
    f.write(f"duration_seconds: {duration:.2f}\n")
    f.write(f"duration_hms: {duration_str}\n")

trainer.save_model(args.output_dir)
tokenizer.save_pretrained(args.output_dir)