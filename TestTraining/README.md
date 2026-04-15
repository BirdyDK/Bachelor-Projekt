# Install
``` pip install torch transformers datasets peft accelerate bitsandbytes trl ```

# Training
There are 5 training scripts:
- runExperiment.py: This is used to run large experiments with focus on trying every combination based on: model, learning rate, rank, and effective bacth size. It uses the training scripts: trainA.py and trainB.py
- trainA.py: This is used for training a model without the use of chat template and takes parameters of the settings used for running experiments.
- trainB.py: This is used for training a model with the use of chat template and takes parameters of the settings used for running experiments.
- testTrainA.py: This script is very similar to trainA.py, but doesn't take any parameters.
- testTrainB.py: This script is very similar to trainB.py, but doesn't take any parameters.

In order to run any of the script you have to call ``` python <script>.py ```

# Use Model
There are 2 use scripts:
- run_all_evaluations.py: This is used when you want to generate an output for many trained models one after another based on the mode: llama, smol, and qwen. This is determined by the start of the folder name within the folder Results.
- use_mystery.py: This is used when you want to get an output for a specific model with a specific adapter and input and is used for single case use.

In order to run any of the script you have to call ``` python <script>.py ```