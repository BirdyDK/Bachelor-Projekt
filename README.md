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


## Generating Quests with the SLM and Rule-Based PCG
The Procedural Quest Generator can be used in two modes: **interactive** (default) and **non‑interactive** (for automation). It supports a **rule‑based** generator (using world state relations) and a **fine‑tuned SLM** (Small Language Model) that produces quests from **reduced** world data. The full world state is too large for the SLM, so it is always reduced before inference.

### Interactive Mode

Run the generator without any flags:

```sh
python main.py
```

This starts an interactive command prompt. Available commands (case‑insensitive):

| Command | Description |
|---------|-------------|
| `LD <filename>` | Load a different world data file (from `pcg/world_data/` or a full path). Example: `LD large_world_data.csv` |
| `GQ PCG` | Generate all eligible quests using the **rule‑based** PCG system and save them to `pcg/output/` |
| `GQ SLM` | Pick a random NPC or faction, reduce the world state around it, then query the SLM. The reduced JSON input is printed before the generated quest. |
| `GQ SLM FOCUS <name>` | Focus on a specific NPC or faction (case‑insensitive), reduce the world, then query the SLM. Example: `GQ SLM FOCUS Fenella`. The reduced JSON input is printed. |
| `GQ SLM INPUT` | Export a reduced world state (random focus) to a JSON file in `pcg/output/` (no SLM query). |
| `GQ SLM INPUT FOCUS <name>` | Export a reduced world state focused on a specific NPC or faction to a JSON file. |
| `EXIT` / `QUIT` | Close the program |

By default, `template_world_data.csv` is loaded. The world data stays in memory, so you can run commands multiple times after switching data files without restarting.

### Non‑Interactive Mode (One‑Shot Generation)

Use the `--gq_pcg` flag to generate rule‑based quests and exit immediately:

```sh
python main.py --gq_pcg
```

You can also specify a particular world data file:

```sh
python main.py --gq_pcg --world_data_file large_world_data.csv
```

If no `--world_data_file` is given, the generator loads `template_world_data.csv`.

### SLM‑Based Generation & RAG Reduction

The SLM (fine‑tuned on `HuggingFaceTB/SmolLM2-1.7B-Instruct`) cannot handle the full world state. Therefore, before sending data to the SLM, the system **reduces** the world to a focused subset:

- **When focusing on an NPC**: includes the NPC, its faction, one disliked NPC (prioritising a different faction), and the enemy’s faction.
- **When focusing on a faction**: includes the faction, one enemy faction, one member from the focus faction, and one enemy NPC from the enemy faction.

All relations are filtered to only those between the included entities. Locations and owned items are limited to the selected NPCs. The player’s event log (`PlayerLog`) is removed to keep the context clean.

The reduced JSON is then sent to the SLM, which produces a quest in the format:

```json
{"Quest": {"Name": "...", "Giver": "...", "Actions": [...]}}

(plain text description)
```

Both `GQ SLM` and `GQ SLM FOCUS` print the exact JSON input given to the SLM – useful for debugging or for offline use by a colleague who has the trained model.

### Output Files

All outputs are saved in `pcg/output/`:

- `generated_quests.json` – Raw quest data from the rule‑based PCG (targets, steps, rewards, favorability).
- `generated_quests_with_hooks.json` – Same quests plus a natural‑language `hook` field.
- `slm_input_full.json` – Full world state as compact JSON (deprecated – use reduced exports instead).
- `slm_input_npc_<name>.json` / `slm_input_faction_<name>.json` – Reduced world states exported with `GQ SLM INPUT FOCUS` or `GQ SLM INPUT`.

### Adding Custom World Data

Place your `.csv` files (following the format of `template_world_data.csv`) into the `pcg/world_data/` folder. You can then load them interactively with `LD` or via the `--world_data_file` flag.

### Requirements

Install the necessary packages:

```sh
pip install torch transformers peft
```

The rule‑based PCG does not require any extra libraries beyond the Python standard library and the packages above for the SLM.

### Architecture

- `parser.py` – Reads the custom `.csv` format and converts relation strings to integers.
- `world_state.py` – Provides access to game state and relation calculations.
- `quest_generator.py` – Rule‑based quest generation using eligibility thresholds and atomic actions.
- `quest_hook_generator.py` – Natural‑language hook generation from template files.
- `world_reducer.py` – Creates reduced world states for the SLM (prioritises cross‑faction enemies).
- `slm_interface.py` – Loads the fine‑tuned SLM and runs inference.
- `main.py` – Interactive and command‑line interface.

### Example Session

```text
> python main.py
Loading world data from: template_world_data.csv

Interactive mode active. Commands (case‑insensitive):
  LD <filename>                 – Load a different world data file
  GQ PCG                        – Generate quests using rule‑based PCG
  GQ SLM                        – Random focus + SLM query
  GQ SLM FOCUS <name>           – Specific focus + SLM query
  GQ SLM INPUT                  – Export reduced world (random focus)
  GQ SLM INPUT FOCUS <name>     – Export reduced world (specific focus)
  EXIT / QUIT                   – Exit

> LD large_world_data.csv
Loading world data from: large_world_data.csv
Switched to world data: large_world_data.csv

> GQ SLM FOCUS Fenella
Focus: npc 'Fenella'
Generating quest using SLM with reduced world data...

--- Input to SLM ---
{"NPCs":{"Fenella":{"Name":"Fenella","Species":"Tiefling","Role":"Thief","CurrentLocation":"Shadowfen","HomeLocation":"Shadowfen","OwnedItems":{"Poison Vial":2,"Throwing Knife":3},"Faction":"The Crimson Covenant","Relations":[{"Target":"The Dusk Syndicate","Favorability":25},{"Target":"Wren","Favorability":18}]},"Wren":{"Name":"Wren","Species":"Elf","Role":"Scout","CurrentLocation":"Mistwood","HomeLocation":"Shadowfen","OwnedItems":{"Elven Bow":1,"Herb Bundle":3},"Faction":"The Dusk Syndicate","Relations":[{"Target":"Fenella","Favorability":18}]}},"Factions":{"The Crimson Covenant":{"Name":"The Crimson Covenant","Relations":[{"Target":"The Dusk Syndicate","Favorability":30}],"Default_Location":"Ironhold"},"The Dusk Syndicate":{"Name":"The Dusk Syndicate","Relations":[{"Target":"The Crimson Covenant","Favorability":30}],"Default_Location":"Shadowfen"}},"Locations":{"Shadowfen":{"Name":"Shadowfen","Enemies":["Cultist","Vampire Spawn"],"Resources":["Poison Vial","Throwing Knife"]},"Mistwood":{"Name":"Mistwood","Enemies":["Shadow Wolf","Giant Spider"],"Resources":["Herb Bundle","Elven Bow"]},"Ironhold":{"Name":"Ironhold","Enemies":["Bandit","Ogre"],"Resources":["Iron Sword","Steel Shield"]}},"Player":{"Species":"Human","FactionRelations":[{"Target":"The Crimson Covenant","Favorability":-25},{"Target":"The Dusk Syndicate","Favorability":-40}],"NPCRelations":[{"Target":"Fenella","Favorability":-40},{"Target":"Wren","Favorability":-25}]}}
----------------------

=== SLM Generated Quest ===
{"Quest": {"Name": "A Poisoned Alliance", "Giver": "Fenella", "Actions": ["goto Shadowfen", "stealth Wren", "take Poison Vial", "goto Ironhold", "give Poison Vial Fenella"]}}

Fenella wants you to steal a poison vial from Wren in Shadowfen and bring it to her in Ironhold.
===========================
```