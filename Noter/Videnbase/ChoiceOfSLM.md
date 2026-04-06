## Selection of Small Language Model (SLM)

### Requirements and Constraints

The selection of a suitable Small Language Model (SLM) was guided by both functional requirements and project constraints. A key requirement was compatibility with a future Retrieval-Augmented Generation (RAG) pipeline. This necessitated the use of an instruction-tuned (Instruct) model, as such models are specifically optimized to follow structured prompts and produce controlled, task-oriented outputs.

Additionally, the project imposed constraints on:

* Computational resources
* Training time
* Model interpretability and controllability

Therefore, the model needed to balance performance with efficiency while remaining feasible to adapt within the project timeframe.

### Candidate Models

Two instruction-tuned SLMs were selected for evaluation:

* **Llama 3.2 1B Instruct**
* **Qwen 2.5 0.5B Instruct**

These models were chosen due to their relatively small parameter sizes, open availability, and suitability for local experimentation.

To ensure a fair comparison, both models were evaluated using identical test scripts and a dataset provided by the project supervisor. The evaluation focused on output quality, coherence, instruction-following capability, and development effort required to achieve acceptable performance.

### Experimental Observations

#### Instruction Following and Output Quality

A significant difference was observed in how the two models handled structured prompts:

* **Llama 3.2 1B Instruct** demonstrated strong zero-shot instruction-following capabilities. It consistently produced coherent and complete outputs with minimal prompt engineering.
* **Qwen 2.5 0.5B Instruct**, in contrast, required substantially more detailed prompting. It often failed to complete sentences or produced fragmented responses when instructions were not explicitly specified.

This indicates that Llama has a stronger understanding of task structure, which is critical in a RAG setting where prompts may vary dynamically.

#### Prompt Sensitivity

The Qwen model exhibited high sensitivity to prompt design:

* Required explicit formatting instructions
* Needed additional context to produce usable outputs
* Struggled with generalization across slightly varied inputs

Llama, on the other hand:

* Performed reliably with simpler prompts
* Required less manual tuning
* Generalized better across different inputs in the dataset

#### Training vs. Adaptation Effort

An important practical consideration was the trade-off between:

* Fine-tuning/training a model
* Prompt engineering and adapting a model

Although Qwen is smaller (0.5B parameters), the effort required to make it produce stable and usable outputs was significant. The team estimated that:

> The time required to sufficiently adapt Qwen through prompt engineering would be comparable to the time required to fine-tune Llama on a small dataset.

This finding reduced the expected advantage of Qwen’s smaller size.

### Model Selection

Based on the experimental evaluation, **Llama 3.2 1B Instruct** was selected as the primary model for the project.

The decision was based on the following factors:

* **Superior instruction-following ability**, reducing the need for complex prompt engineering
* **More coherent and complete outputs**, especially in structured tasks
* **Lower development overhead**, despite having a larger parameter size

While Qwen 2.5 0.5B offers advantages in model size and potential efficiency, its limitations in output reliability and higher adaptation cost made it less suitable within the project scope.

### Implications for RAG Integration

The choice of Llama 3.2 1B Instruct is expected to simplify the integration of a RAG pipeline. Since RAG systems rely on dynamically retrieved context, the language model must:

* Interpret context correctly without excessive prompt engineering
* Generate structured and complete responses
* Maintain consistency across varying inputs

Llama’s observed robustness makes it a more reliable component in such a system.

---

# Appendix

## Scripts
Script used for Llama and first qwen attempt:
```Python
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
```

Modifed for better qwen response (Tested with epochs 2 and 5):
```Python
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
```

## Input/Output

### Script 1

#### Llama
```
### Instruction: Create a mystery story from these details:
Who: Silas the Blacksmith. Where: The Forge. Victim: Mayor Higgins.

### Response: OPENING SCENE SETTING:
The Forge is a whirlwind of heat and clanging metal as Silas the Blacksmith works, his hands moving with the precision of a surgeon. His eyes, however, are sharp and wary, scanning the room for hidden threats. Suddenly, the door bursts open with a crash, and a figure stumbles in, eyes wide with shock. It's Garrett the Smuggler, his voice a booming shout that echoes off the walls. "There's been a murder! The mayor's been found dead in the town square!"

---

PLOT SUMMARY:
In the bustling town, the murder of Mayor Higgins sends shockwaves through the community. Silas the Blacksmith, with his secret dealings in stolen goods, is initially suspected due to his proximity to the crime scene and his known animosity towards Garrett, who owes him a significant amount of money. However, the true culprit is revealed to be Charlie the Carpenter, who murdered the mayor to prevent his own criminal activities from being exposed by Filius, the town's unofficial spy. Filius, aware of Charlie's illicit activities, threatened to report him to the authorities unless Charlie's smuggling operations continued. As investigators delve deeper, they uncover testimony from townspeople, including Alice, who confesses to seeing Charlie lurking around the square on the night of the murder, and Eva, who reveals her knowledge of Filius's espionage activities. The investigation unravels through a series of testimonies and physical evidence, ultimately pointing to Charlie's desperate act to maintain his criminal empire.

---

INVESTIGATION CLUES:
1. Clue 1: A piece of parchment with Mayor Higgins's name and a list of debts, found near the body, suggesting a transaction or blackmail plot. (Points to: Silas the Blacksmith)     

2. Clue 2: A wooden plank with traces of sawdust and a faint scent of fresh wood shavings, matching the type used by blacksmiths, discovered near the mayor's body. (Points to: Silas the Blacksmith)

3. Clue 3: A hastily scribbled note in the mayor's handwriting found in the town well, warning of "secrets that must remain buried" and signed with the initials "C.C.", suggesting a personal vendetta. (Points to: Charlie the Carpenter)

---

RED HERRING:
Silas the Blacksmith's wary demeanor and the presence of stolen goods in his possession make him an obvious suspect, especially as his secretive dealings with Garrett suggest a possible motive for murder.
```
#### Qwen
```
### Instruction: Create a mystery story from these details:
Who: Silas the Blacksmith. Where: The Forge. Victim: Mayor Higgins.

### Response:
**Story:**

The oppressive weight of silence in the forge hung heavy in the air, each breath a fragile note in the silence of the city. Silas stood rigid, his expression unreadable as he surveyed the molten masses that coiled around him. "You don't know the weight of your silence," he murmured, his voice clipped and unyielding. "But I don't want to be found like you are."

Mayor Higgins's eyes narrowed, his gaze sharp and calculating. "Silas, you know what your silence does for me," he said, his tone smooth yet menacing. "Your words unravel my trust, and I fear you'll soon be seen as a traitor."

Silas's expression shifted, his voice soft yet urgent. "I fear the same fate awaits you, Mayor. If your secrets are exposed, the city will unravel just like it does when your shadow is too large."  

The forge pulsed with unspoken truths, secrets that Silas held tightly. "And what of those who lie beneath your coat, Mayor? Do they know your name?" His words were a calculated threat, a silent promise of consequences.

As silence settled, the truth unraveled: Mayor Higgins had been lying about his whereabouts, fearing exposure of his secrets, and Silas had unknowingly uncovered these lies. The confrontation at the forge became a pivotal moment, sealing the fate of both men.

**End of Story.**

---

**Review:**
The story is a masterclass in weaving tension and secrets, with Silas's calculated threat and Mayor Higgins's calculated menace creating a web of intrigue. The forge setting adds a sense of claustrophobia, while their confrontation reveals their hidden agendas. The resolution ties their individual fears to a larger city conspiracy, ensuring the story's closure is both satisfying and impactful.

---

**Alternative Response:**
**Story:**

Silas stood rigid in the dim glow of the forge, his gaze fixed on the molten pieces around him. "You think your silence is as secure as it sounds?" he asked, his voice edged with urgency. "What if the city learns of your dealings?"

Mayor Higgins scoffed, his voice a calculated murmur. "Silas, your words unravel my trust. I fear exposure of your secrets will make me lose control."

Silas's eyes narrowed, his words sharp. "And what of those who lie beneath your coat, Mayor? Do they know your name?" He gestured to the molten masses, his words a silent threat.

The truth was not lost on them. Mayor Higgins had been lying about his whereabouts to protect his own secrets, fearing exposure. Silas, too aware of his own silences, found his knowledge of the city's hidden truths hidden in his words. Their confrontation at the forge became a pivotal moment, unraveling their entanglements and revealing the delicate balance of secrets within the city.

**End of Story.**

---

Both versions successfully craft a mystery story around Silas and Mayor Higgins, with a focus on their covert conflicts and revelations. The first story provides a gripping narrative with rich character interactions, while the second emphasizes the weight of silence and the city's secrets. The choice between them depends on which narrative style best serves the story's goals.

---
**Final Choice:**
**Story:**

The oppressive silence in the forge hangs heavy in the air, each breath a fragile note in the city's shadow. Silas stood rigid, his voice clipped and unyielding. "You don't know the weight of your silence," he murmured, his gaze steady. "But I don't want to be found like you are."

Mayor Higgins's eyes narrowed, his voice a calculated murmur. "Silas, you know what your silence does for me," he said, his tone smooth yet threatening. "Your words unravel my trust, and I fear you'll soon be seen as a traitor."

Silas's eyes flickered with urgency. "I fear the same fate awaits you, Mayor. If your secrets are exposed, the city will unravel just like it does when your shadow is too large."

Silas's words were a calculated threat, a silent promise of consequences. The forge pulsed with unspoken truths, secrets that Silas held tightly. "And what of those who lie beneath your coat, Mayor?" his voice soft yet urgent.

As silence settled, the truth unraveled: Mayor Higgins had been lying about his whereabouts to protect his own secrets, fearing exposure. Silas, too aware of his own silences, found his knowledge of the city's hidden truths hidden in his words. Their confrontation at the forge became a pivotal moment, sealing the fate of both men.

**End of Story.**

---
**Justification:**
This final story effectively weaves Silas's calculated threats and Mayor Higgins
```

### Qwen modified

#### Qwen epochs 2
```
Input: Who: Eleanor the Librarian. Where: The Library. Victim: Professor Aldridge. Method: stabbing.

📖 Generated Mystery:
OPENING.SCENE:
TheLibrary is shrouded in an eerie silence as the sun sets, casting long shadows across its walls. Eleanor the Library's Patron stands at the threshold, her eyes fixed intently on a shelf filled with ancient documents. "These records," she murmurs, voice smooth yet edged with menace, "carry too much weight." Her words hang heavy in the air, setting the stage for what lies to come.

Suddenly, the door bursts open, and Dean rushes inside, his face pale under the dim light. "There's been a murder!" he gasps, breath ragged. "Professor Aldridge... found dead in the study..." His words hang between choppy whispers, leaving the air thick with dread and unspoken truths.     

---

PLOT SUMMARY:
In the shadowed depths of The Library, amidst the towering oak shelves and whispered conversations, the murder unfolds. As Dean emerges, clutching a lifeless figure, the chilling revelation shatters the quiet moment, linking back to the tangled web of secrets that once entwined the town. Initially, suspicion falls on Dean due to his known dealings and the sudden discovery of blood on his clothes—a piece of fabric matching those found near the crime scene. However, it is revealed that the real murderer was the true culprit; it was Alice, who had discovered the identity of Ingrid's true nature through their forbidden magic practices, believing it to be a divine act to protect certain secrets.

Eleanor the Librarianship becomes pivotal when her knowledge about the town’s web of deceit surfaces, hinting at the broader conspiracy. Her testimony, overheard by Greta, inadvertently reveals how Bob manipulated everyone to keep secrets, including Alice’s secret past, thereby creating an opportunity for Charlie to eliminate Professor Aldred. This motive, intertwined with the theft of Ingris’s precious herbs, becomes clear when Greta recalls seeing Alice arguing with him earlier, just before the murder occurred. Further investigation uncovers a scrap of parchment bearing Alice’s handwriting, linked to the diary of a young boy whose name matches that of the victim, ultimately pointing investigators to Alice and her connection to the murder.

---


INVESTIGATION Clues:
1. Clue 1: A torn page from a history book is discovered near the scene, detailing the theft and mentioning the presence of mysterious figures not associated with the murder. (Points to: Dean)

2. Climate: The night is unusually cold, and the shadows around the murder site suggest a tense atmosphere where secrets linger more than daylight might reveal. (Focuses on: Alice)

3. Testimony: Greta mentions overhearing Alice laughing in the library, but laughing wasn’t enough to hide the fear she was hiding—she seemed genuinely distressed. (Indicates: Alice's guilt)

---

RED HErringer Explanations:
1) "The night is shroudded in the scent of old secrets, and when Dean rushes into the room, whispering urgently, the air crackles with the weight of forgotten alliances, one suspects the truth is closer than meets the eye." — Eleanor the Patron

2) "A sighful sigh breaks the tension, breaking the chilling silence when Charlie stumbles upon the scene—a man cloaked in robes and looking visibly shaken, his voice a sharp command echoing off the wooden beams. 'Find me, or I'll do everything in my power to silence you.'" — Dean the Townsperson

📋 Extracted Sections:

PLOT_SUMMARY:
In the shadowed depths of The Library, amidst the towering oak shelves and whispered conversations, the murder unfolds. As Dean emerges, clutching a lifeless figure, the chilling revelation shatters t...

INVESTIGATION_CLUES:
1. Clue 1: A torn page from a history book is discovered near the scene, detailing the theft and mentioning the presence of mysterious figures not associated with the murder. (Points to: Dean)

2. C...
```

#### Qwen epochs 5
```
...
```