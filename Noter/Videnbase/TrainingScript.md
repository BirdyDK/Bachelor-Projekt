# Imports and Environment Setup
```python
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
```
- **Library Imports:** This block imports all the necessary Python libraries.
    - `torch`: The core PyTorch library, which is the foundation for most deep learning work. https://huggingface.co/docs/datasets/en/use_with_pytorch
    - `os`: Used to interact with the operating system, primarily for reading environment variables.
    - `datasets`: A Hugging Face library for easily downloading and loading machine learning datasets. https://huggingface.co/docs/datasets/en/loading
    - `transformers`: The main Hugging Face library for working with thousands of pre-trained models. It provides the classes for models, tokenizers, and training configurations.
    - `peft`: The Parameter Efficient Fine-Tuning library. It allows you to adapt large pre-trained models without fine-tuning all of their parameters, using methods like LoRA.
    - `trl`: The Transformer Reinforcement Learning library. Here, we are using its SFTTrainer (Supervised Fine-tuning Trainer), which is a high-level trainer specifically designed for instruction-tuning language models.
    - `huggingface_hub`: Provides tools to interact with the Hugging Face Hub, such as logging in to access gated models.
    - `dotenv`: A library to load environment variables from a .env file, keeping sensitive information like API tokens out of your main script.

- **CUDA Check:** This diagnostic block checks if a compatible NVIDIA GPU (CUDA) is available. Training a model, even a small one, is practically impossible on a CPU, so this confirms the necessary hardware is present.

- **Load Environment:** load_dotenv() reads the .env file and loads variables (like HF_TOKEN) into the script's environment.

# Setup and Data Loading
```python
# 1. SETUP & DATA
MODEL_ID = "meta-llama/Llama-3.2-1B-Instruct" # You can change to Gemma-2b or others
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
```

- **Configuration:** It sets the MODEL_ID (a model from the Llama-3.2 family hosted on Hugging Face), retrieves the ACCESS_TOKEN from the environment, and defines the path to the local CSV_FILE.

- **Hub Login:** This uses the token to authenticate with the Hugging Face Hub. This is necessary because models from Meta (like Llama) are often "gated," meaning you must agree to their terms of use and log in to download them .

- **Dataset Loading:** load_dataset('csv', ...) loads your local CSV file. The parameters sep=';' and quotechar='"' specify that the CSV is semicolon-delimited and uses double quotes for text fields that may contain special characters. https://huggingface.co/docs/datasets/en/loading

- **Data Formatting:** This is a crucial step. The format_mystery function takes a single example (a row from the CSV) and formats it into a single text string that follows a specific prompt template.
    - It assumes the CSV has columns input_names_only (the prompt/instruction) and output (the desired story). https://huggingface.co/docs/datasets/en/process#map
    - It structures the text as:
        ```
        ### Instruction: Create a mystery story from these details:
        [content of input_names_only]

        ### Response: [content of output]
        ```
        This template mimics the format used to train instruction-tuned models. The model will learn to generate the text after ### Response: when given the text before it .
    - The .map() function applies this formatting to every example in the dataset, creating a new "text" field that the trainer will use.

# Load Model in 4-Bit (Memory Efficient)
```python
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
```
- **4-bit Quantization Config:** This is where the "Q" in QLoRA comes from. BitsAndBytesConfig configures how the model will be quantized (compressed) to reduce its memory footprint dramatically .
    - `load_in_4bit=True`: This tells the library to load the model's weights in 4-bit precision instead of the standard 32-bit or 16-bit.
    - `bnb_4bit_quant_type="nf4"`: Specifies the type of 4-bit quantization to use. "nf4" stands for 4-bit NormalFloat, a data type optimized for normally distributed weights and shown to perform better than standard 4-bit integers .
    - `bnb_4bit_compute_dtype=torch.bfloat16`: This is the data type used for actual computations. While the weights are stored in 4-bit, they are dequantized to bfloat16 just for the mathematical operations. bfloat16 is a good trade-off between performance and numerical stability on modern GPUs .

- **Model Loading:** `AutoModelForCausalLM.from_pretrained` is the standard way to load a causal language model (like Llama) from the Hub .
    - `quantization_config=bnb_config`: It applies the 4-bit configuration we just created.
    - `device_map="auto"`: This lets the accelerate library automatically decide how to distribute the model's layers across available hardware (GPU(s), CPU, etc.) to maximize efficiency .
    - `trust_remote_code=True`: This is sometimes required for newer or custom model architectures that aren't yet integrated into the main transformers release. It allows the script to execute custom code from the model's repository. Use with caution, but it's common for models like the latest Llama.

- **Tokenizer Loading:** The tokenizer is loaded separately. It converts text into numbers (tokens) that the model can understand and numbers back into text .

- **Set Pad Token:** Many models are not trained with a specific padding token. Setting tokenizer.pad_token = tokenizer.eos_token tells the tokenizer to use the "End of Sequence" token for padding, which is a common and safe practice.

# Configure LoRA (The PEFT part)
```python
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
```
- **Prepare for k-bit Training:** `prepare_model_for_kbit_training` is a utility function from PEFT that prepares a quantized model for training. It typically does two things: 1) It casts non-trainable parts of the model (like layer norms) back to a higher precision (e.g., `float32`) for stability, and 2) It enables gradient checkpointing to further save memory .

- **LoRA Configuration (`LoraConfig`):** LoRA is a technique that freezes the original model weights and injects trainable, low-rank matrices (adapters) into specific layers of the model. This is what makes fine-tuning very large models feasible on consumer hardware .
    - `r=32`: This is the rank of the low-rank matrices. A higher `r` means more trainable parameters and potentially more capacity to learn, but also uses more memory. Common values are 8, 16, 32, 64.
    - `lora_alpha=64`: This is a scaling factor. The output of the LoRA layers is scaled by lora_alpha / r. A higher value gives more weight to the new adapter weights .
    - `target_modules="all-linear"`: This specifies which parts of the model to apply LoRA to. In the original QLoRA paper, it was found that targeting all linear layers (attention layers, feed-forward layers, etc.) significantly improves performance, matching full fine-tuning. The `"all-linear"` shortcut is a convenient way to do this without having to list all the layer names manually .
    - `lora_dropout=0.1`: Dropout probability for the LoRA layers to prevent overfitting.
    - `task_type="CAUSAL_LM"`: Specifies the type of task, which is Causal Language Modeling (predicting the next token) .

- **Get PEFT Model:** `get_peft_model` takes the original, quantized model and the `peft_config` and wraps them into a single PEFT model object that is ready for training. After this, only the LoRA adapter parameters will be trainable.

# Train
```python
# 4. TRAIN
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    args=TrainingArguments(
        output_dir="./mystery_adapter",
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        num_train_epochs=3,
        logging_steps=10,
        bf16=True, # Set to False if using CPU/older GPU
        save_strategy="epoch"
    ),
)

trainer.train()
model.save_pretrained("./TestTraining")
print("Training Complete! Adapter saved to ./TestTraining")
```
- **SFTTrainer:** This is a specialized trainer from the trl library, designed to simplify supervised fine-tuning. It automatically handles formatting, tokenization, and packing of the data for causal language modeling .
    - `model`: The PEFT model we prepared.
    - `train_dataset`: The formatted dataset containing the "text" field.
    - `args=TrainingArguments(...)`: This object from the transformers library holds all the hyperparameters for training .
        - `output_dir`: Where to save checkpoints and the final model.
        - `per_device_train_batch_size=2`: The batch size per GPU. This is low due to memory constraints .
        - `gradient_accumulation_steps=4`: This simulates a larger batch size. Instead of updating the model's weights after every 2 samples, it accumulates gradients over 4 steps and then updates, resulting in an effective batch size of 2 * 4 = 8. This is a key memory-saving technique .
        - `learning_rate=2e-4`: The learning rate for the optimizer.
        - `num_train_epochs=3`: The model will pass through the entire dataset 3 times.
        - `logging_steps=10`: Print training loss every 10 steps.
        - `bf16=True`: Enables bfloat16 mixed precision training for faster computation and lower memory usage. This requires a relatively modern GPU (like Ampere or newer) .
        - `save_strategy="epoch"`: Save a checkpoint of the model at the end of every epoch.
    - `trainer.train()`: This single line starts the training loop.

- **Save Adapter:** After training, `model.save_pretrained(...)` saves only the small LoRA adapter weights (a few megabytes), not the entire 1B parameter base model. This makes the fine-tuned model easy to store and share . The final print statement confirms the completion.