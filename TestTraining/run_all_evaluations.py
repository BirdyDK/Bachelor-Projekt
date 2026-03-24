import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

RESULTS_ROOT = "./TestTraining/results"
OUTPUT_FILE = "trainingResults2.md"

TEST_INPUT = "Who: Silas the Blacksmith. Where: The Forge. Victim: Mayor Higgins."

def solve_mystery(model, tokenizer, input_text):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a mystery writer. Always respond with a story containing these exact "
                "sections: OPENING SCENE:, PLOT SUMMARY:, INVESTIGATION CLUES:, and "
                "RED HERRING EXPLANATION:. Each section must start with the heading on its own line."
            )
        },
        {
            "role": "user",
            "content": f"Create a mystery story from these details:\n{input_text}"
        }
    ]



    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )


    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=1000,
        temperature=0.7,
        do_sample=True
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def detect_base_model(folder_name):
    """Infer which base model was used from the folder name."""
    if "Llama-3.2-1B-Instruct" in folder_name:
        return "meta-llama/Llama-3.2-1B-Instruct"
    if "Qwen2.5-0.5B-Instruct" in folder_name:
        return "Qwen/Qwen2.5-0.5B-Instruct"
    if "SmolLM2-1.7B-Instruct" in folder_name:
        return "HuggingFaceTB/SmolLM2-1.7B-Instruct"
    raise ValueError(f"Could not detect base model for: {folder_name}")


def main():
    result_folders = sorted(
        f for f in os.listdir(RESULTS_ROOT)
        if os.path.isdir(os.path.join(RESULTS_ROOT, f))
    )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("# Training Results\n\n")

        for folder in result_folders:
            full_path = os.path.join(RESULTS_ROOT, folder)
            adapter_path = full_path

            print(f"\n=== Evaluating {folder} ===")

            # Detect which base model to load
            base_model = detect_base_model(folder)

            # Load base model + tokenizer
            tokenizer = AutoTokenizer.from_pretrained(base_model)
            model = AutoModelForCausalLM.from_pretrained(
                base_model,
                torch_dtype=torch.float16,
                device_map="auto"
            )

            # Load LoRA adapter
            model = PeftModel.from_pretrained(model, adapter_path)
            model.eval()

            # Run evaluation
            output_text = solve_mystery(model, tokenizer, TEST_INPUT)

            # Write to markdown
            out.write(f"## {folder}\n")
            out.write(f"**Base Model:** {base_model}\n\n")
            out.write("**Output:**\n")
            out.write("```\n")
            out.write(output_text)
            out.write("\n```\n\n")

            print(f"✓ Completed {folder}")

    print("\nAll evaluations complete. Results saved to trainingResults.md")


if __name__ == "__main__":
    main()
