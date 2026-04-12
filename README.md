# Bachelor-Projekt: Game-State-Aware SLM for Procedural Quest Generation in Video Games

## Preliminary Problem Statement
### Problem Description: 
Procedurally generating quests in an open-world RPG video game setting, like Skyrim or Shadow of War, generally rely on specific templates or components being matched together. This greatly limits their complexity, makes them repetitive, and they often feel unrelated to the player. Our goal is to see if it is possible to make a Small Language Model (SLM) that can generate quests of greater variety and of more relevance to the player while running on their own machine. The core challenge is to ensure that the generated quests are narratively consistent, respect the giving NPC's role and how it relates to the player, and, most crucially, are mechanically possible within the current game world-state (e.g., targeting existing items, locations, and characters). 

### Project Hypothesis: 
We believe that by leveraging a RAG-enhanced SLM we can generate quests that are completable by the player, while increasing narrative and gameplay variety compared to regular template-based systems. The model will be trained on artificially created game-state data, fabricated quests, and output criteria. While we don’t intend to implement it in a game in this project, we will put some thought into how the output could be formatted to interface with a game.

## Paper
The paper is written in LaTeX in the Overleaf program and be found here: https://www.overleaf.com/project/6985d47bee63fb2990113ad1.
This is also where we will be keeping our bibliography.


## Setting up the program
### Virtual Environment
#### Set Up
This should only be done one per project.\
Make sure you're cd'ed into the project folder.\
Give the command:

```sh
python -m venv .venv
```

The venv can from then on be activated the first command for powershell or the second for wsl:

```sh
./.venv/Scripts/Activate.ps1

source .venv/bin/activate
```

If you get permission issues, check your permissions in an admin powershell. You can then set it with the second command. It needs to be `RemoteSigned`, but you can probably fiddle with the scope as shown [here](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy?view=powershell-7.5).

```sh
Get-ExecutionPolicy -List

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```



Once your venv is running (indicated by green bit before the powershell path) run:

```sh
python -m pip install --upgrade pip
```

If you get `No module named pip` then try this:

```sh
python -m ensurepip --upgrade
```

Then you need to check what CUDA version your GPU, if you have one, is. This determines what torch package you need.\
Run the following command and scroll up to the top to see it.

```sh
nvidia-smi
```

If you have a CUDA, then run first of the following commands where you replace `XXX` with your version number (12.6 -> 126).\
If you don't have CUDA, then run the second command.

```sh
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cuXXX

pip3 install torch torchvision
```

Finally, run this command to install any remaining packages.

```sh
pip install -r requirements.txt
```

#### Regular Use
The vscode extension [Python Environments](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-python-envs) makes it easy to activate the environment. Just close your terminal and open it again (the latter can be done with `ctrl + æ`).

If that doesn't work, then the activation command can be used to activate it as well.

If you need to deactivate it, you can just run the command `deactivate`.

### Setting up the Model
To set up the model you need a `.env` file in root.
In it, make sure to define the following env_var: `HF_TOKEN = "YOUR_HUGGING_FACE_LLAMA_TOKEN_HERE"


## Quest Generator
Run the quest generator with

```sh
python ./quest_generator/main.py
```

and then run

```sh
python ./quest_generator/generate_displays.py
```

to get the output in a human readable format.

## PCG

The Procedural Quest Generator can be used in two modes: **interactive** (default) and **non‑interactive** (for automation).

### Interactive Mode

Run the generator without any flags:

```sh
python main.py
```

This starts an interactive command prompt. Available commands (case‑insensitive):

`LD <filename>` – Load a different world data file (from `pcg/world_data/` or a full path).
Example: `LD large_world_data.csv`

`GQ PCG` – Generate all eligible quests using the currently loaded world data and save them to `pcg/output/`.

`EXIT` or `QUIT` – Close the program.

By default, `template_world_data.csv` is loaded. The world data stays in memory, so you can run `GQ PCG` multiple times after switching data files without restarting.

Non‑Interactive Mode (One‑Shot Generation)
Use the `--gq_pcg` flag to generate quests and exit immediately:

```sh
python main.py --gq_pcg
```

You can also specify a particular world data file:

```sh
python main.py --gq_pcg --world_data_file large_world_data.csv
```

If no `--world_data_file` is given, the generator loads `template_world_data.csv`.

Output Files
Both modes produce two JSON files in `pcg/output/`:

`generated_quests.json` – Raw quest data (targets, steps, rewards, favorability).

`generated_quests_with_hooks.json` – Same quests plus a natural‑language hook field, ready for in‑game dialogue.

Adding Custom World Data
Place your .csv files (following the format of `template_world_data.csv`) into the `pcg/world_data/` folder. You can then load them interactively with `LD` or via the `--world_data_file` flag.
