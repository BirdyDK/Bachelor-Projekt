---
base_model: openai-community/gpt2
library_name: peft
pipeline_tag: text-generation
tags:
- base_model:adapter:openai-community/gpt2
- lora
- sft
- transformers
- trl
---
# Install
``` pip install torch transformers datasets peft accelerate bitsandbytes trl ```

# Run Training
``` python train_mystery.py ```

# Use Model
``` python use_mystery.py ```
### Framework versions

- PEFT 0.18.1