# CoIN++ Training Scripts

This folder contains the final LLaVA continual-training entrypoints for the consolidated CoIN++ Factor-1 dataset.

## Dataset Defaults

- data root: `/home/chencheng/data/Code/Easy_Train_MLLM/cl_dataset/coin_factor1_final`
- image folder: `/home/chencheng/data/Code/Easy_Train_MLLM/cl_dataset`

Each factor uses the fixed `10000 train + 1000 eval` splits under:

```bash
cl_dataset/coin_factor1_final/splits/<factor>/trainable/train/<stage>/train.json
cl_dataset/coin_factor1_final/splits/<factor>/trainable/eval/<stage>/eval.json
```

## Main Commands

```bash
# Evidence complexity, default order: single -> multi -> cross-region/multihop -> cross-context
bash scripts/coin++/run_evidence_complexity_llava.sh

# Visual substrate
bash scripts/coin++/run_visual_substrate_llava.sh

# Skill requirement
bash scripts/coin++/run_skill_requirement_llava.sh

# Run all three factor tracks
bash scripts/coin++/run_all_factor_tracks_llava.sh
```

## Smoke Run

```bash
INCLUDE_GPUS=localhost:0 MAX_STEPS=2 bash scripts/coin++/run_smoke_llava.sh
```

## Evidence Evaluation

Run evaluation in the same environment used for training:

```bash
conda activate ETrain
```

Alternatively, provide its interpreter explicitly with
`PYTHON_BIN=/path/to/ETrain/bin/python`.


Run a small inference check before the complete evaluation:

```bash
LIMIT=20 RESULT_ROOT=results/coin++/evidence_complexity/eval_smoke \
  bash scripts/coin++/run_evidence_complexity_eval_llava.sh
```

Run the complete 4-checkpoint by 4-task evaluation sequentially on one GPU:

```bash
bash scripts/coin++/run_evidence_complexity_eval_llava.sh
```

Use four GPUs to evaluate the four checkpoints in parallel:

```bash
PARALLEL_STAGES=1 EVAL_GPUS=0,1,2,3 \
  bash scripts/coin++/run_evidence_complexity_eval_llava.sh
```

Completed stage results are skipped by default. Set `SKIP_COMPLETED=0` to
force re-evaluation. Summary matrices and forgetting results are written under
`results/coin++/evidence_complexity/eval/summary/`.

## Skill + Visual End-to-End Run

Train and evaluate Skill Requirement first, then train and evaluate Visual
Substrate, with no manual hand-off between scripts:

```bash
conda activate ETrain
bash scripts/coin++/run_skill_visual_train_eval_llava.sh
```

Training uses GPUs `0-7`. Evaluation also uses GPUs `0-7` and schedules one
checkpoint per GPU in batches. Skill evaluation runs its 10 checkpoints as an
`8 + 2` schedule, while Visual evaluates all 6 checkpoints in one batch.

Useful controls include `RUN_SKILL_TRAIN`, `RUN_SKILL_EVAL`,
`RUN_VISUAL_TRAIN`, `RUN_VISUAL_EVAL`, `SKILL_RESUME_FROM_STAGE`,
`VISUAL_RESUME_FROM_STAGE`, `SKIP_COMPLETED_TRAIN`, `SKIP_COMPLETED_EVAL`,
`EVAL_GPUS`, and `EVAL_LIMIT`.

## Trainable-Module Study

Run the Visual-only, Projector-only, and LLM-only regimes sequentially on the
same Visual Substrate transition:

```bash
conda activate ETrain
bash scripts/coin++/run_trainable_modules_llava.sh
```

Run one regime, switch the fixed data transition, or include the optional
all-module regime:

```bash
MODULE_MODE=vision_only bash scripts/coin++/run_trainable_module_cl_llava.sh
MODULE_MODE=llm_only FACTOR=skill_requirement \
  bash scripts/coin++/run_trainable_module_cl_llava.sh
MODULE_MODES="vision_only projector_only llm_only llm_projector all_modules" \
  bash scripts/coin++/run_trainable_modules_llava.sh
```

The default effective batch size is kept at 256 on eight GPUs. Vision-bearing
regimes use batch/accumulation `2/16`; the others use `4/8`. Default learning
rates are `2e-6` for Vision, `2e-5` for Projector, and `2e-4` for LLM LoRA.
Every checkpoint records the exact trainable-parameter count and retains the
fixed pretrained projector for reproducible continuation and evaluation.

Module-study checkpoints and logs are written to:

```bash
checkpoints/LLaVA/Instruction/CoIN++_TrainableModules/<factor>/<mode>/
results/coin++_trainable_modules/<factor>/<mode>/logs/
```

Evaluate every completed checkpoint from every module regime on the full task
matrix, then generate a cross-module comparison:

```bash
conda activate ETrain
bash scripts/coin++/run_trainable_modules_eval_llava.sh
```

For a non-interactive training container, select the environment explicitly:

```bash
PYTHON_BIN=/root/miniconda3/envs/ETrain/bin/python \
  bash scripts/coin++/run_trainable_modules_eval_llava.sh
```

Run a small validation first or evaluate a different factor/mode set:

```bash
LIMIT=10 RESULT_BASE=results/coin++_trainable_modules_smoke \
  bash scripts/coin++/run_trainable_modules_eval_llava.sh
FACTOR=skill_requirement MODULE_MODES="vision_only projector_only llm_only" \
  bash scripts/coin++/run_trainable_modules_eval_llava.sh
```

Per-mode learning matrices and forgetting tables are written below
`results/coin++_trainable_modules/<factor>/<mode>/eval/summary/`. The combined
comparison is written to
`results/coin++_trainable_modules/<factor>/comparison/module_comparison.md`.

Evaluation selects GPUs with at least 20 GB free memory by default and batches
checkpoints when fewer GPUs are available. Override this behavior when needed:

```bash
EVAL_GPUS=2,3,4,7 bash scripts/coin++/run_trainable_modules_eval_llava.sh
MIN_FREE_GPU_MB=24000 bash scripts/coin++/run_trainable_modules_eval_llava.sh
```

## Important Overrides

```bash
MODEL_VERSION=vicuna-13b-v1.5          # default is vicuna-7b-v1.5
MODEL_PATH=/path/to/base               # override full base model path
PROJECTOR_PATH=/path/to/mm_projector.bin
INCLUDE_GPUS=localhost:0,1,2,3,4,5,6,7
PER_DEVICE_BATCH=4
GRAD_ACCUM=8
NUM_TRAIN_EPOCHS=1
MAX_STEPS=200                          # optional; unset means epoch mode
RESET_EACH_STAGE=1                     # train each stage from base, not continual chain
RESUME_FROM_STAGE=3                    # continue from an interrupted chain
STAGES_OVERRIDE="single_evidence multi_evidence"
```

## Output Layout

Default checkpoints:

```bash
checkpoints/LLaVA/Instruction/CoIN++/<factor>/<stage_no>_<stage>/
```

Default logs:

```bash
results/coin++/<factor>/logs/<stage_no>_<stage>.log
```

The default mode is true continual learning: stage 2 uses `--previous_task_model_path` from stage 1, stage 3 uses stage 2, and so on. Set `RESET_EACH_STAGE=1` only for non-continual ablations.
