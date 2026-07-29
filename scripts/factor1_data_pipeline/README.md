# Factor-1 Data Pipeline Scripts

This is the canonical location for scripts used to construct the CoIN++
Factor-1 dataset. The former root-level copies have been removed.

## Main Stages

1. Build raw metadata from downloaded datasets: `factor1_coin_meta.py`, `run_factor1_all_metadata.sh`.
2. Audit VLM/rule labels: `audit_factor1_labels.py`, `score_factor1_label_audit.py`.
3. Select and refine targeted relabel pools: `select_factor1_targeted_relabel_candidates.py`, `run_factor1_targeted_relabel_*.sh`.
4. Convert/merge into LLaVA JSON: `convert_factor1_meta_to_llava.py`, `merge_factor1_llava_train_json.py`.
5. Repair/canonicalize labels: `repair_factor1_evidence_skill_labels.py`, `canonicalize_factor1_train_json.py`, `canonicalize_factor1_diagram_skill.py`.
6. Build balanced factor splits: `build_factor1_balanced_splits.py`, `run_build_factor1_10k_splits.sh`.
7. Validate final distribution and image paths: `check_factor1_final_distribution.py`, `run_check_factor1_final_v8.sh`.

## Current Final Dataset

Use this as the stable dataset root for training:

```bash
DATA_ROOT=/home/chencheng/data/Code/Easy_Train_MLLM/cl_dataset/coin_factor1_final
IMAGE_FOLDER=/home/chencheng/data/Code/Easy_Train_MLLM/cl_dataset
```

## Running The Pipeline

Each shell entrypoint resolves the repository root from this directory, so it
can be run directly from the repository root:

```bash
bash scripts/factor1_data_pipeline/run_check_factor1_final_v8.sh
```

Set `PROJECT_ROOT` only when invoking the pipeline through a symlink or from a
non-standard checkout layout.
