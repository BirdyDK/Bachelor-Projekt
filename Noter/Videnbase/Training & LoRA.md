# LoRA – Core Concept (Hu et al., 2021)
* Full fine-tuning updates all weights → high memory (gradients + optimizer states).
* LoRA freezes pretrained weights ( W ).
* Weight update modeled as low-rank decomposition:

$$
W' = W + BA
$$

* $r \ll d,k$
* Only ( A ) and ( B ) are trainable.

### Key Insight from Paper
* Fine-tuning updates are empirically low-rank.
* Adaptation lies in a low-dimensional subspace.
* Small ( r ) sufficient → major parameter reduction.

### Practical Effects
* ↓ Trainable parameters
* ↓ GPU memory
* ↓ Optimizer states
* No inference latency increase
* Small adapter checkpoints

# LoRA Hyperparameters – Logical Effects
## Rank (r = 32)
* Controls adapter capacity.
* Higher r:

  * ↑ expressiveness
  * ↑ memory
  * ↑ overfitting risk
* Lower r:

  * ↑ efficiency
  * ↓ flexibility

Paper: performance saturates at relatively low ranks.

→ r=32 = moderate capacity / efficiency trade-off.

## Alpha (α = 64)
Scaling rule:

$$
\Delta W = \frac{\alpha}{r} BA
$$

* Controls update magnitude.
* Your ratio: 64/32 = 2.

Higher α:
* Stronger adaptation
* Risk of instability

Lower α:
* Conservative updates
* Slower learning

## Target Modules: "all-linear"
* LoRA applied to all linear layers (not only attention).
* ↑ adaptation flexibility.
* ↑ trainable parameters.
* Better creative adaptation.

Trade-off: slightly higher memory vs attention-only LoRA.

# Optimization Setup
## Learning Rate (3e-5)
* Only adapters are trained → stable training.
* Too high → unstable updates.
* Too low → slow convergence.

3e-5 = conservative and stable.

## Effective Batch Size
* Batch size = 2
* Gradient accumulation = 4

Effective batch size = 8

Effect:
* Smoother gradients
* Lower memory usage
* Slower wall-clock per update

## Epochs = 1
* Small dataset.
* LoRA adapts quickly.
* Multiple epochs → overfitting risk.

# Efficiency Logic
## Without LoRA
* All parameters trainable.
* Large optimizer states.
* High VRAM usage.

## With LoRA
* Only small matrices trained.
* Frozen base model.
* Massive reduction in memory & checkpoint size.

---
# Sources
- LoRA paper: https://arxiv.org/abs/2106.09685
- Training script: TestTraining/train_mystery.py