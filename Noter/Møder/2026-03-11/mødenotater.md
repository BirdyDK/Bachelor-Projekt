# Model training
* Note down every change and what we have tried when training the model, was there any success or fails.
* Look back at the experiments with Qwen and see how the training changed with all of the changes made.
    * The change in training script
    * Less given information for generating quest
    * Learning rate, epochs
* If sentences are incomplete look at learning rate and how much data is trained on, it can be undertrained in which we increase the learning (epochs).

# Quests
* What do we want to achieve with the quests (Game State.drawio), make sure to only have what is necessary and not have too much data for the SLM to remember and learn.
* How do we want to structure the quests as with the murder mystery when looking at input/output for a SLM. Is less information better or is more information better (We can look at the findings for model trained on murder mystery).
* How do we plan on doing the quest:
    * Procedureal -> flavour with SLM
    * SLM based on quest of Procedural structure
