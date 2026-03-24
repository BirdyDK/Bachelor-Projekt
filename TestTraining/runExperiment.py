import os
import sys
import subprocess

# Use the SAME Python interpreter that runs this script
PY = sys.executable

# --- Configuration ---
PHYSICAL_BATCH_SIZE = 4
EXPERIMENTS = []

# Define Hyperparameter Grid
models = [
    {"id": "Qwen/Qwen2.5-0.5B-Instruct", "script": "./TestTraining/trainB.py"},
    {"id": "HuggingFaceTB/SmolLM2-1.7B-Instruct", "script": "./TestTraining/trainB.py"}
]

# Grid variables
target_effective_batches = [8, 16, 32]
learning_rates = [2e-4, 3e-5, 5e-5]
r_values = [16, 32, 64]

# Generate Experiments (Approx 27 tests per model)
for model in models:
    for eff_bs in target_effective_batches:
        for lr in learning_rates:
            for r in r_values:
                accum = eff_bs // PHYSICAL_BATCH_SIZE

                model_name = model["id"].split('/')[-1]
                folder_name = f"{model_name}_ebs{eff_bs}_lr{lr}_r{r}"
                out_dir = f"./TestTraining/results/{folder_name}"

                EXPERIMENTS.append({
                    "script": model["script"],
                    "model": model["id"],
                    "batch": PHYSICAL_BATCH_SIZE,
                    "accum": accum,
                    "lr": lr,
                    "r": r,
                    "alpha": r * 2,
                    "out_dir": out_dir
                })

# --- Execution Loop ---
print(f"Total experiments planned: {len(EXPERIMENTS)}")

for exp in EXPERIMENTS:
    os.makedirs(exp["out_dir"], exist_ok=True)

    cmd = [
        PY,  # ← THIS is the fix
        exp["script"],
        "--model_id", exp["model"],
        "--batch_size", str(exp["batch"]),
        "--grad_accum", str(exp["accum"]),
        "--learning_rate", str(exp["lr"]),
        "--lora_r", str(exp["r"]),
        "--lora_alpha", str(exp["alpha"]),
        "--output_dir", exp["out_dir"]
    ]

    print(f"\n>>> RUNNING: {exp['out_dir']}")
    print(f">>> Config: LR={exp['lr']}, Rank={exp['r']}, Eff_BS={exp['batch']*exp['accum']}")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print(f"!!! Experiment failed: {exp['out_dir']} !!!")
        continue
